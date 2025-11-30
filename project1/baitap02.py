from pygments.formatters.html import webify
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

#khoi tao
driver = webdriver.Chrome()

# Mở full màn hình 
driver.maximize_window()

#Mo trang 
url = "https://en.wikipedia.org/wiki/List_of_painters_by_name"
driver.get(url)

#Doi khoang chung 2 giay
time.sleep(2)

#Lay tat ca cac the <a>
tags = driver.find_elements(By.XPATH, "//a[contains(@title, 'List of painters')]")

#Tao ra danh sach lien ket
links = [tag.get_attribute("href") for tag in tags]

#xuat thong tin
for link in links:
    print(link)


#Dong webdriver
driver.quit()
