import logging
import asyncio
import json
from crawler_service import CrawlerService
from rabbitmq_service import RabbitMQService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    host = "https://www.olx.co.id"
    url = "/mobil-bekas_c198"

    crawler = CrawlerService(logger)
    # car_details_service = CarDetailsService(logger)
    publisher = RabbitMQService()
    publisher.declare_queue()

    async for car in crawler.crawl_olx_cars(host, url):
        # car_details = await car_details_service.get_car_details(host, car['url'])
        # if car_details:
        #     car.update(car_details)
        # cars.append(car)
        publisher.send_message('store_head',  json.dumps(car))
        
        # rms.send_message('crawl_detail',  json.dumps(car))
        # db_saver.save_car(car)
        # logger.info({car})
        logger.info(f"Store car: {car['brand']} {car['model']} to saving")

    # logger.info(f"Scraped all car header processing to the database.")

if __name__ == "__main__":
    asyncio.run(main())
