from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver import ActionChains
import time
import pandas as pd
import getpass


# Đường dẫn đến file thực thi geckodriver
gecko_path = r"D:/Khanh/hoc/ma nguon mo/crawl/selenium/project2/geckodriver.exe"

# Khởi tởi đối tượng dịch vụ với đường geckodriver
ser = Service(gecko_path)

# Tạo tùy chọn
options = webdriver.firefox.options.Options();
options.binary_location ="C:/Program Files/Mozilla Firefox/firefox.exe"
# Thiết lập firefox chỉ hiện thị giao diện
options.headless = False

# Khởi tạo driver
driver = webdriver.Firefox(options = options, service=ser)
# Tạo url
url = 'https://x.com/i/flow/login'

# Truy cập
driver.get(url)

# Tạm dừng khoảng 2 giây
time.sleep(3)

# Nhap thong tin nguoi dung
my_email = input('Please provide your email:')
my_password = getpass.getpass('Please provide your password:')

firstname_input = driver.find_element(By.XPATH, "//input[@name='username']")
lastname_input = driver.find_element(By.XPATH, "//input[@name='password']")
actionChains = ActionChains(driver)
time.sleep(1)


for i in range(2):
    actionChains.send_keys(Keys.TAB)

actionChains.send_keys(my_email)
actionChains.send_keys(Keys.TAB)
actionChains.send_keys(my_password)
actionChains.send_keys(Keys.ENTER)

actionChains.perform()
time.sleep(10)

tweets = driver.find_elements(By.CSS_SELECTOR, '[data-testid="tweet"]')
for tweet in tweets:
    tag_text = tweet.find_element(By.CSS_SELECTOR,'div[data-testid="User-Names"]').text
    name, handle, _, timestamp = tag_text.split('\n')
    tweet_text = tweet.find_element(By.CSS_SELECTOR,'div[data-testid="tweetText"]').text
    retweet_count = tweet.find_element(By.CSS_SELECTOR,'div[data-testid="retweet"]').text
    like_count = tweet.find_element(By.CSS_SELECTOR,'div[data-testid="like"]').text
    reply_count = tweet.find_element(By.CSS_SELECTOR,'div[data-testid="reply"]').text
    print(name, handle)
    print(tweet_text)
    print("--------------")


driver.quit()