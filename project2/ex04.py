from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver import ActionChains
import time
import pandas as pd
import getpass

driver = webdriver.Chrome()

# Tạo url
url = 'https://www.reddit.com/login/'



# Truy cập
driver.get(url)
time.sleep(10)

# Nhap thong tin nguoi dung
my_email = input('Please provide your email:')
my_password = getpass.getpass('Please provide your password:')


actionChains = ActionChains(driver)
time.sleep(1)
for i in range(6):
    actionChains.key_down(Keys.TAB).perform()
    
actionChains.send_keys(my_email).perform()
actionChains.key_down(Keys.TAB).perform()

actionChains.send_keys(my_password + Keys.ENTER).perform()

time.sleep(5)



# Truy cap trang post bai
url2 = 'https://www.reddit.com/r/kpro2210/?type=TEXT'
driver.get(url2)
time.sleep(2)


for i in range(18):
    actionChains.key_down(Keys.TAB).perform()


actionChains.send_keys('Vi du post').perform()
actionChains.key_down(Keys.TAB).perform
actionChains.key_down(Keys.TAB).perform()

actionChains.send_keys('Do Quoc').perform()

for i in range(8):
    actionChains.key_down(Keys.TAB).perform()
    time.sleep(1)

actionChains.send_keys(Keys.ENTER).perform()


time.sleep(10)
driver.quit()