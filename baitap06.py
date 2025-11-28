from pygments.formatters.html import webify
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pandas as pd
import re


# Tạo dataframe rỗng
all_links = []
d = pd.DataFrame({'name': [], 'birth': [], 'death': [], 'nationality': []})

#Khởi tạo Webdriver
for i in range(70, 71):

    driver = webdriver.Chrome()
    url = "https://en.wikipedia.org/wiki/List_of_painters_by_name_beginning_with_%22"+chr(i)+"%22"
    try:
        #Mo trang
        driver.get(url)
        #Doi time de tai trang

        time.sleep(2)

        ul_tags = driver.find_elements(By.TAG_NAME, "ul")
        ul_painters = ul_tags[19]
        li_tags = ul_painters.find_elements(By.TAG_NAME, "li")

        links = [tag.find_element(By.TAG_NAME, "a").get_attribute("href") for tag in li_tags]


        for x in links:
            all_links.append(x)
    except:
        print("Error!")
print(len(all_links))
driver.quit()
count = 0
for link in all_links:
    if (count > 3):
        break
    count = count+1;

    print(link)
    try:
        driver = webdriver.Chrome()
        url = link
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
            birth_element = driver.find_element(By.XPATH,"//table[contains(@class,'infobox')]//th[.='Born']/following-sibling::td")
            birth_text = birth_element.text
            birth = re.findall(r'[0-9]{1,2}\s+[A-Za-z]+\s+[0-9]{4}', birth_text)[0]
        except:
            birth = ""

        # Lấy ngày mất
        try:
            death_element = driver.find_element(By.XPATH,"//table[contains(@class,'infobox')]//th[.='Died']/following-sibling::td")
            death_text = death_element.text
            death = re.findall(r'[0-9]{1,2}\s+[A-Za-z]+\s+[0-9]{4}', death_text)[0]
        except :
            death = ""

        # Lấy quốc tịch 
        # try:
        #     nationality_element = driver.find_element(By.XPATH, "//*[@class='IPA-label IPA-label-small']")
        #     nationality = nationality_element.text.strip(":")
            
        # except:
        #     nationality = ""
        # Lấy birthplace
        try:
            nationality_element = driver.find_element(By.CSS_SELECTOR, "table.infobox .birthplace")
            nationality = nationality_element.text.strip(":")
        except:
            nationality = ""

        # Tạo dict thông tin hoạ sĩ
        painter = {'name': name, 'birth': birth, 'death': death, 'nationality': nationality}

        # Chuyển dict thành dataframe
        painter_df = pd.DataFrame([painter])

        # Thêm vào df chính
        d = pd.concat([d, painter_df], ignore_index=True)

        # Đóng webdriver
        driver.quit()
    except:
        pass

# In ra DF
print(d)
file_name = 'Painters.xlsx'

d.to_excel(file_name)
print('DataFrame is written to Excel File successfully. ')