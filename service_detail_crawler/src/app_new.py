import logging
import json
import asyncio
from rabbitmq_service import RabbitMQService
from crawler_service import CrawlerService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    crawler = CrawlerService(logger)
    car_detail = await crawler.crawl_detail_olx_cars('https://www.olx.co.id/item/honda-mobilio-e-cvt-15cc-2014-at-tdp-85k-hub-sahid-iid-929394042')
    logger.info(car_detail)


if __name__ == "__main__":
    asyncio.run(main())

    