from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import time
import pandas as pd
import re

# DataFrame kết quả
d = pd.DataFrame({'name': [], 'birth': [], 'death': [], 'nationality': []})

# 1) Lấy link painter trong list theo chữ cái
all_links = []
#Khởi tạo Webdriver
for i in range(70, 71):
    driver = webdriver.Chrome()
    url = "https://en.wikipedia.org/wiki/List_of_painters_by_name_beginning_with_%22P%22"
    try:
        driver.get(url)

        time.sleep(2)

        content = driver.find_element(By.CSS_SELECTOR, "#mw-content-text .mw-parser-output")
        painter_links = content.find_elements(By.CSS_SELECTOR, "div.div-col ul li a[title]")

        links = [a.get_attribute("href") for a in painter_links]
        for x in links:
            all_links.append(x)
    except:
        print("Error!")

    driver.quit()
print(len(all_links))

# 2) Vào từng trang painter để lấy thông tin chi tiết
count = 0
for link in all_links:
    if (count >3):   
        break
    count = count +1;
    
    print(link)
    try:
        driver = webdriver.Chrome()
        url = link
        driver.get(url)

        time.sleep(2)

        # Tên họa sĩ
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
            death_element = driver.find_element(By.XPATH,"//table[contains(@class,'infobox')]//th[.='Died']/following-sibling::td")
            death_text = death_element.text
            death = re.findall(r'[0-9]{1,2}\s+[A-Za-z]+\s+[0-9]{4}', death_text)[0]
        except :
            death = ""

        # Lấy quốc tịch 
        try:
            nationality_element = driver.find_element(By.CSS_SELECTOR, "table.infobox .birthplace")
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


        driver.quit()
    except:
        pass

print(d)

file_name = 'PaintersA.xlsx'
d.to_excel(file_name, index=False)
print('DataFrame is written to Excel File successfully.')
