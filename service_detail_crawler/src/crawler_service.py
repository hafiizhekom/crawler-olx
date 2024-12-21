from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from bs4 import BeautifulSoup
import logging
import re
import json

class CrawlerService:
    def __init__(self, logger=None, max_retries=3):
        self.logger = logger or logging.getLogger(__name__)
        self.max_retries = max_retries
    
    async def crawl_detail_olx_cars(self, url):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=['--disable-http2', '--no-sandbox'])
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            )
            page = await context.new_page()
            
            for attempt in range(self.max_retries):
                try:
                    self.logger.info(f"Attempting to navigate to {url}")
                    await page.goto(url, wait_until='networkidle', timeout=60000)
                    self.logger.info(f"Successfully loaded {url}")
                    
                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    await page.wait_for_timeout(2000)
                    
                    content = await page.content()
                    soup = BeautifulSoup(content, 'html.parser')
                    await self.save_html_to_file(content, "playwright/output", "olx_detail.txt")
                    self.logger.info("Parsing page content")

                    if soup:
                        scriptElements = soup.find_all('script', {'type': 'text/javascript'})
                        print("scriptElements")
                        print(scriptElements)
                        scriptElementsPrint = "\n".join([str(element) for element in scriptElements])
                        await self.save_html_to_file(scriptElementsPrint, "playwright/output", "scriptElements.txt")

                        
                        if scriptElements:
                            for i, script in enumerate(scriptElements):
                                
                                script_content = script.string or str(script)
                                await self.save_html_to_file(script_content, "playwright/output", f"script{i}.txt")
                                match = re.search(r'window\.__APP\s*=\s*({.*?});', script_content, re.DOTALL)
            
                                if match:
                                    json_string = match.group(1)

                                    cleaned_text = re.sub(r'\s+', ' ', json_string)  # Remove extra whitespace
                                    cleaned_text = cleaned_text.replace('props:', '"props":')
                                    cleaned_text = cleaned_text.replace('states:', '"states":')
                                    cleaned_text = cleaned_text.replace('config:', '"config":')
                                    json_data = json.loads(cleaned_text)

                                    elements_parameter = json_data['states']['items']['elements']
                                    next_key_elements_parameter = list(elements_parameter.keys())[0]
                                    elements_parameter = elements_parameter[next_key_elements_parameter]
                                    car_attributes_detail = elements_parameter['parameters']
                                    car_image_detail = elements_parameter['images']

                                    color = car_attributes_detail[6]['value_name']
                                    body_type = car_attributes_detail[8]['value_name']
                                    seller_type = car_attributes_detail[10]['value_name']
                                    car_exchange = car_attributes_detail[11]['value_name']

                                    car_images_detail = []
                                    for image in car_image_detail:
                                        car_images_detail.append(image['url'])

                                    return True, {
                                        'color': color,
                                        'body_type': body_type,
                                        'seller_type': seller_type,
                                        'car_exchange': car_exchange,
                                        'images': car_images_detail,
                                    }                                 
                    
                except PlaywrightTimeoutError:
                    self.logger.warning(f"Timeout on attempt {attempt + 1}")
                except Exception as e:
                    self.logger.error(f"Error on attempt {attempt + 1}: {str(e)}")
                
                await page.wait_for_timeout(5000)
            
            await browser.close()
            return False, None
