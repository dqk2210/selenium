from selenium import webdriver
from selenium.webdriver.common.by import By
import time

driver = webdriver.Chrome()
driver.maximize_window()

url = "https://en.wikipedia.org/wiki/List_of_painters_by_name_beginning_with_%22P%22"
driver.get(url)

time.sleep(2)

content = driver.find_element(By.CSS_SELECTOR, "#mw-content-text .mw-parser-output")
painter_links = content.find_elements(By.CSS_SELECTOR, "div.div-col ul li a[title]")

links = [a.get_attribute("href") for a in painter_links]
titles = [a.get_attribute("title") for a in painter_links]

for link in links:
    print(link)

for title in titles:
    print(title)

driver.quit()
