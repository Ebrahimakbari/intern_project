import time, django, json, random, os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pytz

#Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()
from news.serializers import NewsSerializer


class ZoomitScraper:
    """Selenium-based web scraper for Zoomit"""
    def __init__(self, json_path="news_output.json"):
        """Initialize the scraper."""
        self.json_path = json_path
        self.driver = None
        self._initialize_json_file()
        
        # Random user agents
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        ]
        
    def _initialize_json_file(self):
        """Create json file if not exists."""
        if not os.path.exists(self.json_path):
            with open(self.json_path, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    def _random_delay(self, min=2, max=5):
        """Random delay."""
        time.sleep(random.uniform(min, max))
    
    def _initialize_driver(self):
        """Set up Selenium WebDriver"""
        options = webdriver.ChromeOptions()
        
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument(f"user-agent={random.choice(self.user_agents)}")
        
        #TODO: Download and Update the chromedriver patch for dockerize 
        service = Service(executable_path='/home/ebrahim/Desktop/projects/INTERN/chromedriver-linux64/chromedriver')
        # service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.set_page_load_timeout(30)
        self.driver.set_script_timeout(20)
    
    def _get_page(self, url):
        """Load a page."""
        try:
            self.driver.get(url)
            self._random_delay()
            WebDriverWait(self.driver, 10).until(lambda d: d.execute_script("return document.readyState") == "complete")
        except Exception as e:
            print(f"Error: {str(e)}")
    
    def _extract_article_data(self, url):
        """Extract article data from a single news page."""
        data = {
            "title": "",
            "content": "",
            "tags": [],
            "source": url,
        }
        
        # Extract title
        title = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        data["title"] = title.text.strip()
        
        # Extract tags
        h1_elem = self.driver.find_element(By.TAG_NAME, 'h1')
        parent_elem = h1_elem.find_element(By.XPATH, './..')
        tag_elements = parent_elem.find_elements(By.XPATH, './/a[span]')
        data['tags'] = [
            span.text.strip() 
            for a_tag in tag_elements 
            for span in a_tag.find_elements(By.TAG_NAME, 'span')
            if span.text.strip()
        ]

        # Extract content
        article = self.driver.find_element(By.TAG_NAME, "article")
        first_div = article.find_element(By.XPATH, "./div[1]")
        sixth_child_div = first_div.find_element(By.XPATH, "./div[5]")
        paragraphs = sixth_child_div.find_elements(By.TAG_NAME, "p")
        if len(paragraphs) == 0:
            sixth_child_div = first_div.find_element(By.XPATH, "./div[4]")
            paragraphs = sixth_child_div.find_elements(By.TAG_NAME, "p")
        data["content"] = '\n'.join([p.text.strip() for p in paragraphs if p.text.strip()])
        return data
    
    def _save_data(self, data):
        """Save scraped data into database using serializer and Json file."""
        serializer = NewsSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            with open(self.json_path, 'r+', encoding='utf-8') as f:
                existing_data = json.load(f)
                existing_data.append(
                    {**data,"scraped_at": datetime.now(tz=pytz.timezone('Asia/Tehran')).isoformat()}
                    )
                f.seek(0)
                json.dump(existing_data, f, ensure_ascii=False, indent=2)
            print(f"DONE: {data['title']}")
        else:
            print(f"PASS: {serializer.errors}")

    def scrape_archive(self, archive_url="https://www.zoomit.ir/archive/"):
        """Main method to scrape news."""
        self._initialize_driver()
        self._get_page(archive_url)        

        # Get all article links
        links = self.driver.find_elements(By.CSS_SELECTOR, "div.scroll-m-16 a")
        urls = [
            a.get_attribute('href') 
            for a in links 
            if a.get_attribute('href') and not a.find_elements(By.XPATH, ".//span[contains(text(), 'تبلیغات')]")
        ]
        print(f"Found {len(urls)} articles!")
        
        for url in urls:
            self._get_page(url)
            article_data = self._extract_article_data(url)
            if article_data["title"]:
                self._save_data(article_data)
            
            self._random_delay()

        self.driver.quit()
        print("Browser closed!")


if __name__ == "__main__":
    scraper = ZoomitScraper()
    scraper.scrape_archive()