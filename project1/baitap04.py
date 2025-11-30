from builtins import range
from selenium import webdriver
from selenium.webdriver.common.by import By
import time


#Khởi tạo Webdriver
driver = webdriver.Chrome()

for i in range(65, 91):
    url = "https://en.wikipedia.org/wiki/List_of_painters_by_name_beginning_with_%22"+chr(i)+"%22"
    try:
        #Mo trang
        driver.get(url)
        #Doi time de tai
        time.sleep(2)
        content = driver.find_element(By.CSS_SELECTOR, "#mw-content-text .mw-parser-output")
        painter_links = content.find_elements(By.CSS_SELECTOR, "div.div-col ul li a[title]")

        links = [a.get_attribute("href") for a in painter_links]
        titles = [a.get_attribute("title") for a in painter_links]

        for title in titles:
            print(title)
    except:
        print("Error!")
#Dong web
driver.quit()