from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait


#Selenium
options = webdriver.ChromeOptions()
options.add_argument("--headless")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 10)  # Create a WebDriverWait object with a timeout of 10 seconds

driver.get("https://www.zoomit.ir/archive/?sort=Newest&publishDate=All&readingTime=All&pageNumber=1")
wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")

#Link
links = driver.find_elements(By.CSS_SELECTOR, "div.scroll-m-16 a")
urls = [a.get_attribute('href') for a in links if a.get_attribute('href')]

#Main
for url in urls:
    driver.get(url)
    wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")

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
    
    print(data)

driver.quit()