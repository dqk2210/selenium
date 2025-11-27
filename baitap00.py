from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# Tao 1 driver de bat dau dieu khien
driver = webdriver.Chrome()

#Mo mot trang web
driver.get("https://gomotungkinh.com/")
time.sleep(5)


try:
    while True:
        driver.find_element(By.ID, "bonk").click()
        time.sleep(2)
except:
    driver.quit()