import json
import asyncio
import logging
from rabbitmq_service import RabbitMQService
from sqlite_service import SQLiteService


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    
    sqlite_service = SQLiteService()
    sqlite_service.connect()

    consumer = RabbitMQService(queue_name="save_image")
    consumer.declare_queue()

    async def process_message(ch, method, properties, body):
        try:
            if body is not None:
                message = body.decode()
                images = json.loads(message)
                print(f" [x] Received {images}")

                if sqlite_service.save_message(images) :
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                else:
                    logger.info(f"Message requeued after failed saving attempts")
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            else:
                logger.info(f"Message is empty")
                ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            
    def callback_wrapper(ch, method, properties, body):
        asyncio.run(process_message(ch, method, properties, body))

    try:
        consumer.start_consuming(callback_wrapper)
    except KeyboardInterrupt:
        print("Shutting down...")
