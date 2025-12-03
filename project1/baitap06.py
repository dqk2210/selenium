from pygments.formatters.html import webify
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pandas as pd
import re


# Tạo dataframe rỗng
all_links = []
all_nationalities = []
d = pd.DataFrame({'name': [], 'birth': [], 'death': [], 'nationality': []})

def extract_nationality(li_text: str) -> str:
    # Cắt phần sau dấu ) (sau tên + năm sinh/tử)
    parts = re.split(r'\)\s*[,\.]\s*', li_text, maxsplit=1)
    if len(parts) == 2:
        tail = parts[1].strip()
    else:
        tail = li_text

    # Cắt trước các từ chỉ nghề nghiệp
    tail = re.split(
        r'\b(painter|artist|sculptor|printmaker|illustrator|ceramicist|muralist|miniaturist|portraitist|landscape)\b',
        tail,
        maxsplit=1,
        flags=re.IGNORECASE
    )[0]

    return tail.strip(' ,.;')

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

        for tag in li_tags:
            try:
                a_tag = tag.find_element(By.TAG_NAME, "a")
                link = a_tag.get_attribute("href")
                li_text = tag.text
                nationality = extract_nationality(li_text)

                all_links.append(link)              # như code cũ
                all_nationalities.append(nationality)  # quốc tịch tương ứng
            except:
                pass
    except:
        print("Error!")
print(len(all_links))
driver.quit()


count = 0
idx = 0 
for link in all_links:
    if (count > 3):
        break
    count = count+1;

    nationality = all_nationalities[idx]
    idx += 1
    print(link, " | ", nationality)
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
            birth_element = driver.find_element(By.XPATH, "//th[text()='Born']/following-sibling::td")
            birth_text = birth_element.text
            # Trích xuất định dạng ngày (ví dụ: 12 June 1900)
            birth_match = re.findall(r'\b(?:\d{1,2}\s+[A-Za-z]+\s+\d{4}|[A-Za-z]+\s+\d{4}|\d{4})\b', birth_text)
            birth = birth_match[0] if birth_match else ""
        except:
            birth = ""
            
        # 3. Lấy ngày mất (Died)
        try:
            death_element = driver.find_element(By.XPATH, "//th[text()='Died']/following-sibling::td")
            death = death_element.text
            death_match = re.findall(r'\b(?:\d{1,2}\s+[A-Za-z]+\s+\d{4}|[A-Za-z]+\s+\d{4}|\d{4})\b', death)
            death = death_match[0] if death_match else ""
        except:
            death = ""
            
        # # 4. Lấy quốc tịch (Nationality)
        # try:
        #     nationality_element = driver.find_element(By.CSS_SELECTOR, "table.infobox .birthplace")
        #     nationality = nationality_element.text.strip(":")
        # except:
        #     nationality = ""
        

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