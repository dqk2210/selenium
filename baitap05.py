from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pandas as pd
import re

# Tạo dataframe rỗng
d = pd.DataFrame({'name': [], 'birth': [], 'death': [], 'nationality': []})

# Khởi tạo webdriver
driver = webdriver.Chrome()

# Mở trang
url = "https://en.wikipedia.org/wiki/Edvard_Munch"
driver.get(url)

# Đợi 2 giây
time.sleep(2)

# Lấy tên hoạ sĩ (h1)
try:
    name = driver.find_element(By.TAG_NAME, "h1").text
except:
    name = ""

# Lấy ngày sinh
try:
    birth_element = driver.find_element(
        By.XPATH,
        "//table[contains(@class,'infobox')]//th[.='Born']/following-sibling::td"
    )
    birth_text = birth_element.text
    birth = re.findall(r'[0-9]{1,2}\s+[A-Za-z]+\s+[0-9]{4}', birth_text)[0]
except:
    birth = ""

# Lấy ngày mất
try:
    death_element = driver.find_element(
        By.XPATH,
        "//table[contains(@class,'infobox')]//th[.='Died']/following-sibling::td"
    )
    death_text = death_element.text
    death = re.findall(r'[0-9]{1,2}\s+[A-Za-z]+\s+[0-9]{4}', death_text)[0]
except :
    death = ""

# Lấy quốc tịch 
try:
    nationality_element = driver.find_element(By.XPATH, "//*[@class='IPA-label IPA-label-small']")
    nationality = nationality_element.text.strip(":")
    
except:
    nationality = ""

# Tạo dict thông tin hoạ sĩ
painter = {
    'name': name,
    'birth': birth,
    'death': death,
    'nationality': nationality
}

# Chuyển dict thành dataframe
painter_df = pd.DataFrame([painter])

# Thêm vào df chính
d = pd.concat([d, painter_df], ignore_index=True)

# In ra DF
print(d)

# Đóng webdriver
driver.quit()
