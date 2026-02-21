"""
Dynamic Content Scraper with Selenium
Scrapes JavaScript-rendered content and dynamic pages
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DynamicScraper:
    """Scrape dynamically loaded content using Selenium"""

    def __init__(self, headless: bool = True):
        """Initialize Selenium WebDriver"""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            logger.info("✅ WebDriver initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize WebDriver: {e}")
            self.driver = None

    def load_page(self, url: str, wait_time: int = 10) -> bool:
        """Load page and wait for dynamic content"""
        try:
            self.driver.get(url)
            logger.info(f"📄 Loaded {url}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to load {url}: {e}")
            return False

    def wait_for_element(self, selector: str, by: By = By.CSS_SELECTOR, timeout: int = 10) -> bool:
        """Wait for element to be present"""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, selector))
            )
            logger.info(f"✅ Element found: {selector}")
            return True
        except:
            logger.warning(f"⚠️ Element not found within {timeout}s: {selector}")
            return False

    def scroll_to_bottom(self, pause_time: float = 0.5) -> None:
        """Scroll to bottom to load lazy-loaded content"""
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(pause_time)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        logger.info("✅ Scrolled to bottom")

    def extract_elements(self, selector: str, by: By = By.CSS_SELECTOR) -> List[str]:
        """Extract text from multiple elements"""
        try:
            elements = self.driver.find_elements(by, selector)
            return [elem.text for elem in elements if elem.text.strip()]
        except Exception as e:
            logger.error(f"❌ Error extracting elements: {e}")
            return []

    def extract_links(self, selector: str = "a", by: By = By.CSS_SELECTOR) -> List[Dict]:
        """Extract links with href and text"""
        try:
            elements = self.driver.find_elements(by, selector)
            links = []
            for elem in elements:
                href = elem.get_attribute("href")
                text = elem.text.strip()
                if href and text:
                    links.append({"text": text, "url": href})
            return links
        except Exception as e:
            logger.error(f"❌ Error extracting links: {e}")
            return []

    def click_and_wait(self, selector: str, by: By = By.CSS_SELECTOR, wait_selector: str = None) -> bool:
        """Click element and wait for content to load"""
        try:
            element = self.driver.find_element(by, selector)
            element.click()
            logger.info(f"✅ Clicked: {selector}")
            
            if wait_selector:
                self.wait_for_element(wait_selector)
            return True
        except Exception as e:
            logger.error(f"❌ Error clicking element: {e}")
            return False

    def get_page_source(self) -> str:
        """Get current page HTML"""
        return self.driver.page_source

    def take_screenshot(self, filename: str) -> bool:
        """Take screenshot of current page"""
        try:
            self.driver.save_screenshot(filename)
            logger.info(f"📷 Screenshot saved: {filename}")
            return True
        except Exception as e:
            logger.error(f"❌ Screenshot failed: {e}")
            return False

    def close(self) -> None:
        """Close the browser"""
        if self.driver:
            self.driver.quit()
            logger.info("✅ Browser closed")


def demo_scraper():
    """Demo: Scrape a dynamic website"""
    scraper = DynamicScraper(headless=True)
    
    # Example: Scrape quotes from a JavaScript-rendered page
    # (This is pseudocode - adapt to your target website)
    url = "https://quotes.toscrape.com/js/"
    
    if scraper.load_page(url):
        # Wait for quotes to load
        scraper.wait_for_element(".quote")
        
        # Scroll to load more
        scraper.scroll_to_bottom()
        
        # Extract quotes
        quotes = scraper.extract_elements(".text")
        authors = scraper.extract_elements(".author")
        
        print(f"\n📚 Found {len(quotes)} quotes:")
        for quote, author in zip(quotes[:5], authors[:5]):
            print(f"  {quote[:50]}... - {author}")
    
    scraper.close()


if __name__ == "__main__":
    print("🌐 Dynamic Content Scraper with Selenium\n")
    
    print("Features:")
    print("✓ Load JavaScript-rendered pages")
    print("✓ Wait for dynamic elements")
    print("✓ Scroll for lazy-loaded content")
    print("✓ Extract links and text")
    print("✓ Click and interact with pages")
    print("✓ Take screenshots")
    print("\nNote: Requires selenium and chromedriver installed")
    print("pip install selenium webdriver-manager")
