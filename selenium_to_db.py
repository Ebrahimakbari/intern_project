import os
import django
import json
from datetime import datetime

#Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from news.serializers import NewsSerializer


#Selenium
options = webdriver.ChromeOptions()
options.add_argument("--headless")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

#Json
json_path = "news_output.json"
if not os.path.exists(json_path):
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump([], f, ensure_ascii=False, indent=2)

#Target
driver.get("https://www.zoomit.ir/archive/")
driver.implicitly_wait(5)

#Links
links = driver.find_elements(By.CSS_SELECTOR, "div.scroll-m-16 a")
urls = [a.get_attribute('href') for a in links if a.get_attribute('href')]

#Main
for url in urls:
    driver.get(url)
    driver.implicitly_wait(3)
    
    title = driver.find_element(By.TAG_NAME, "h1").text.strip()

    #tags
    try:
        h1_elem = driver.find_element(By.TAG_NAME, 'h1')
        siblings = h1_elem.find_elements(By.XPATH, './following-sibling::div')
        if len(siblings) >= 2:
            tag_div = siblings[1]
            tags = [span.text.strip() for span in tag_div.find_elements(By.CSS_SELECTOR, 'a span')]
        else:
            tags = []
    except:
        tags = []

    # content
    try:
        article = driver.find_element(By.TAG_NAME, "article")
        second_child = article.find_elements(By.XPATH, "./*")[1]  # index 1 for the second child
        sixth_child = second_child.find_elements(By.XPATH, "./*")[5]  # index 5 for the sixth child
        paragraphs = sixth_child.find_elements(By.XPATH, ".//p")  # using // to search across all levels
        content = '\n'.join([p.text.strip() for p in paragraphs if p.text.strip()])
    except Exception as e:
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