from datetime import datetime
import os
import django
import json
import random
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

#Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()
from news.serializers import NewsSerializer

def random_delay(min=2, max=5):
    time.sleep(random.uniform(min, max))

def get_page_with_retry(driver, url):
    try:
        driver.get(url)
        random_delay()
        WebDriverWait(driver, 10).until(lambda d: d.execute_script("return document.readyState") == "complete")
        return True
    except Exception as e:
        print(f"Retrying {url} due to error: {str(e)}")
        raise

#Main Selenium
options = webdriver.ChromeOptions()
options.add_argument("--headless=new")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)

#Random User-Agent
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
]
options.add_argument(f"user-agent={random.choice(user_agents)}")

#Selenium
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
driver.set_page_load_timeout(30)
driver.set_script_timeout(20)

#JSON
json_path = "news_output.json"
if not os.path.exists(json_path):
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump([], f, ensure_ascii=False, indent=2)


if not get_page_with_retry(driver, "https://www.zoomit.ir/archive/"):
    raise Exception("Failed to load archive page")

links = driver.find_elements(By.CSS_SELECTOR, "div.scroll-m-16 a")
urls = [a.get_attribute('href') for a in links if a.get_attribute('href')]

for url in urls:
    if not get_page_with_retry(driver, url):
        continue

    #title
    title = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "h1")))
    title = title.text.strip()

    #tags
    try:
        h1_elem = driver.find_element(By.TAG_NAME, 'h1')
        siblings = h1_elem.find_elements(By.XPATH, './following-sibling::div')
        tag_div = siblings[1] if len(siblings) >= 2 else None
        tags = [span.text.strip() for span in tag_div.find_elements(By.CSS_SELECTOR, 'a span')] if tag_div else []
    except:
        tags = []

    # content
    try:
        article = driver.find_element(By.TAG_NAME, "article")
        paragraphs = article.find_elements(By.XPATH, ".//p")
        content = '\n'.join([p.text.strip() for p in paragraphs if p.text.strip()])
    except:
        content = ''

    #data
    data = {
        "title": title,
        "content": content,
        "tags": tags,
        "source": url,
    }
    #serializer
    serializer = NewsSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        print(f"✅: {title}")
    else:
        print(f"❌: {serializer.errors}")
        continue

    #JSON
    with open(json_path, 'r+', encoding='utf-8') as f:
        existing_data = json.load(f)
        existing_data.append({
            "title": title,
            "content": content,
            "tags": tags,
            "source": url,
            "scraped_at": datetime.now().isoformat()
        })
        f.seek(0)
        json.dump(existing_data, f, ensure_ascii=False, indent=2)

driver.quit()