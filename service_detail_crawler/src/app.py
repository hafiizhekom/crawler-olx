import logging
import json
import asyncio
from rabbitmq_service import RabbitMQService
from crawler_service import CrawlerService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":

    publisher = RabbitMQService(queue_name="save_detail")
    publisher.declare_queue()

    consumer = RabbitMQService(queue_name="crawl_detail")
    # Saat deklarasi antrean utama
    consumer.declare_queue()
    # consumer.channel.basic_qos(prefetch_count=1)

    async def process_message(ch, method, properties, body):
        try:
            if body is not None:
                message = body.decode()
                car = json.loads(message)
                print(f" [x] Received {car}")

                crawler = CrawlerService(logger)
                success, car_detail = await crawler.crawl_detail_olx_cars(car['url'])
                car_image = car['images']
                del car['images']
                if success:
                    logger.info(car_detail)
                    publisher.send_message('save_detail',  json.dumps(car_detail))
                    publisher.send_message('save_image',  json.dumps(car_image))
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                else:
                    logger.info(f"Message requeued after failed crawling attempts")
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            else:
                logger.info(f"Message is empty")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")        

    def callback_wrapper(ch, method, properties, body):
        logger.info("Processing new message...")
        asyncio.run(process_message(ch, method, properties, body))

    try:
        consumer.start_consuming(callback_wrapper)
    except KeyboardInterrupt:
        print("Shutting down...")
    
