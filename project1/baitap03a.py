from selenium import webdriver
from selenium.webdriver.common.by import By
import time

driver = webdriver.Chrome()
driver.maximize_window()

url = "https://en.wikipedia.org/wiki/List_of_painters_by_name_beginning_with_%22P%22"
driver.get(url)

time.sleep(2)

ul_tags = driver.find_elements(By.TAG_NAME, "ul")
print(len(ul_tags))

ul_painters = ul_tags[19]
li_tags = ul_painters.find_elements(By.TAG_NAME, "li")

# links = [tag.find_element(By.TAG_NAME, "a").get_attribute("href") for tag in li_tags]

# titles = [tag.find_element(By.TAG_NAME, "a").get_attribute("title") for tag in li_tags]
links = []
titles = []

for tag in li_tags:
    a_tags = tag.find_elements(By.TAG_NAME, "a")  # KHÁC find_element
    if not a_tags:        # nếu không có <a> thì bỏ qua
        continue
    a = a_tags[0]
    links.append(a.get_attribute("href"))
    titles.append(a.get_attribute("title"))
for link in links:
    print(link)

for title in titles:
    print(title)

driver.close()