from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import re

# DataFrame kết quả
d = pd.DataFrame({'name': [], 'birth': [], 'death': [], 'nationality': []})

# 1) Lấy link painter trong list theo chữ cái
all_links = []

driver = webdriver.Chrome()

try:
    # Ví dụ: chỉ crawl chữ F (như code gốc của anh)
    # Nếu muốn A-Z: for ch in range(ord("A"), ord("Z") + 1):
    for i in range(ord("F"), ord("F") + 1):
        url = f'https://en.wikipedia.org/wiki/List_of_painters_by_name_beginning_with_%22{chr(i)}%22'
        print("Đang mở:", url)
        driver.get(url)

        # Đợi page load
        time.sleep(2)

        # Một cách chọn UL an toàn hơn: chọn ul trong phần nội dung chính
        ul_tags = driver.find_elements(By.CSS_SELECTOR, "div.mw-parser-output ul")

        print("Số ul:", len(ul_tags))
        if len(ul_tags) == 0:
            print("Không tìm thấy ul phù hợp!")
            continue

        # Thường list painter nằm ở các ul sau phần mở đầu → có thể chọn từ 2-3 trở đi
        # Ở đây tạm lấy tất cả <li><a> trong các ul này
        li_tags = []
        for ul in ul_tags:
            li_tags.extend(ul.find_elements(By.TAG_NAME, "li"))

        links = []
        for tag in li_tags:
            try:
                a = tag.find_element(By.TAG_NAME, "a")
                href = a.get_attribute("href")
                # Lọc những link kiểu /wiki/...
                if href and "/wiki/" in href:
                    links.append(href)
            except Exception as e:
                print("Lỗi lấy link trong list:", e)

        print("Số link lấy được:", len(links))
        all_links.extend(links)

finally:
    driver.quit()

# 2) Vào từng trang painter để lấy thông tin chi tiết
driver = webdriver.Chrome()

try:
    count = 0
    for link in all_links:
        if count >= 4:   # test 4 người đầu
            break
        count += 1

        print("Đang crawl:", link)
        try:
            driver.get(link)
            time.sleep(2)

            # Tên họa sĩ
            try:
                name = driver.find_element(By.TAG_NAME, "h1").text
            except:
                name = ""

            # Tìm bảng infobox (nhiều trang không có infobox → bỏ)
            try:
                infobox = driver.find_element(By.CSS_SELECTOR, "table.infobox")
            except:
                infobox = None

            birth = ""
            death = ""
            nationality = ""

            if infobox:
                # Ngày sinh
                try:
                    birth_element = infobox.find_element(
                        By.XPATH, ".//th[contains(text(),'Born')]/following-sibling::td"
                    )
                    birth_text = birth_element.text
                    match = re.findall(r'\d{1,2}\s+[A-Za-z]+\s+\d{4}', birth_text)
                    if match:
                        birth = match[0]
                except Exception as e:
                    print("Lỗi lấy ngày sinh:", e)

                # Ngày mất
                try:
                    death_element = infobox.find_element(
                        By.XPATH, ".//th[contains(text(),'Died')]/following-sibling::td"
                    )
                    death_text = death_element.text
                    match = re.findall(r'\d{1,2}\s+[A-Za-z]+\s+\d{4}', death_text)
                    if match:
                        death = match[0]
                except Exception as e:
                    print("Lỗi lấy ngày mất:", e)

                # Quốc tịch
                try:
                    nationality_element = infobox.find_element(
                        By.XPATH, ".//th[.='Nationality']/following-sibling::td"
                    )
                    nationality = nationality_element.text.strip()
                except Exception as e:
                    print("Lỗi lấy quốc tịch:", e)

            painter = {
                'name': name,
                'birth': birth,
                'death': death,
                'nationality': nationality
            }

            painter_df = pd.DataFrame([painter])
            d = pd.concat([d, painter_df], ignore_index=True)

        except Exception as e:
            print("Lỗi khi crawl trang:", link, "->", e)

finally:
    driver.quit()

print(d)

file_name = 'Painters.xlsx'
d.to_excel(file_name, index=False)
print('DataFrame is written to Excel File successfully.')
