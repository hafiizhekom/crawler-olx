from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from bs4 import BeautifulSoup
import logging

class CrawlerService:
    def __init__(self, logger=None, max_retries=3):
        self.logger = logger or logging.getLogger(__name__)
        self.max_retries = max_retries

    async def crawl_olx_cars(self, host, url):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False, args=['--disable-http2', '--no-sandbox'])
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            )
            page = await context.new_page()
            
            for attempt in range(self.max_retries):
                try:
                    self.logger.info(f"Attempting to navigate to {host+url}")
                    await page.goto(host+url, wait_until='networkidle', timeout=60000)
                    self.logger.info(f"Successfully loaded {host+url}")
                    
                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    await page.wait_for_timeout(2000)
                    
                    content = await page.content()
                    soup = BeautifulSoup(content, 'html.parser')
                    self.logger.info("Parsing page content")

                    car_listings = soup.find_all('li', attrs={'data-aut-id': 'itemBox'})
                    for car in car_listings:
                        title = car.find('div', attrs={'data-aut-id': 'itemTitle'})
                        brand = 'N/A'
                        model = 'N/A'
                        if title:
                            title_text = title.text.strip()
                            title_parts = title_text.split(' ')
                            brand = title_parts[0]
                            model = ' '.join(title_parts[1:])

                        price = car.find('span', attrs={'data-aut-id': 'itemPrice'})
                        price = price.text.strip() if price else 'N/A'
                        price = int(price.replace('Rp', '').replace('.', '').strip())
                        
                        location = car.find('div', attrs={'data-aut-id': 'itemDetails'})
                        location = location.contents[0].strip() if location else 'N/A'

                        url_elem = car.find('a')
                        car_url = url_elem.get('href') if url_elem else 'N/A'

                        yield {'brand': brand, 'model': model, 'price': price, 'location': location, 'url': host+car_url}
                    
                    break

                except PlaywrightTimeoutError:
                    self.logger.warning(f"Timeout on attempt {attempt + 1}")
                except Exception as e:
                    self.logger.error(f"Error on attempt {attempt + 1}: {str(e)}")
                
                await page.wait_for_timeout(5000)
            
            await browser.close()
