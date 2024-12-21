import json
import asyncio
import logging
from rabbitmq_service import RabbitMQService
from sqlite_service import SQLiteService


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def callback(ch, method, properties, body, sqlite_service, publisher):
            message = body.decode()
            car = json.loads(message)
            print(f" [x] Received {car}")
            if car_id_saved := sqlite_service.save_message(car) :
                car_detail_params = {
                      'car_id' : car_id_saved,
                      'url' : car['url']
                }
                publisher.send_message('crawl_detail',  json.dumps(car_detail_params))
                ch.basic_ack(delivery_tag=method.delivery_tag)

if __name__ == "__main__":
    
    sqlite_service = SQLiteService()
    sqlite_service.connect()

    consumer = RabbitMQService(queue_name="store_head")
    consumer.declare_queue()

    publisher = RabbitMQService(queue_name="crawl_detail")
    publisher.declare_queue()

    async def process_message(ch, method, properties, body):
        try:

            message = body.decode()
            car = json.loads(message)
            print(f" [x] Received {car}")

            if car_id_saved := sqlite_service.save_message(car) :
                car_detail_params = {
                      'car_id' : car_id_saved,
                      'url' : car['url']
                }
                publisher.send_message('crawl_detail',  json.dumps(car_detail_params))
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
