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

    consumer = RabbitMQService(queue_name="save_detail")
    consumer.declare_queue()

    async def process_message(ch, method, properties, body):
        try:
            if body is None:
                logger.info("Received None message, acknowledging and not requeuing")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return
            message = body.decode()
            car = json.loads(message)
            print(f" [x] Received {car}")

            if sqlite_service.save_message(car) :
                ch.basic_ack(delivery_tag=method.delivery_tag)
            else:
                logger.info(f"Message requeued after failed saving attempts")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            
    def callback_wrapper(ch, method, properties, body):
        asyncio.run(process_message(ch, method, properties, body))

    try:
        consumer.start_consuming(callback_wrapper)
    except KeyboardInterrupt:
        print("Shutting down...")
