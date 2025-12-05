from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pandas as pd

# DataFrame kết quả (giống cấu trúc painters)
d = pd.DataFrame({
    'name': [],          # Tên trường
    'short_name': [],    # Ký hiệu / tên viết tắt
    'founded': [],       # Ngày thành lập
    'rector': [],        # Hiệu trưởng / Giám đốc
    'website': []        # Website chính thức
})

# ==============================
# 1) LẤY LINK CÁC TRƯỜNG ĐH VN
# ==============================

all_links = []

# Khởi tạo WebDriver
driver = webdriver.Chrome()
url = ("https://vi.wikipedia.org/wiki/Danh_s%C3%A1ch_tr%C6%B0%E1%BB%9Dng_%C4%91%E1%BA%A1i_h%E1%BB%8Dc,_h%E1%BB%8Dc_vi%E1%BB%87n_v%C3%A0_cao_%C4%91%E1%BA%B3ng_t%E1%BA%A1i_Vi%E1%BB%87t_Nam")
try:
    driver.get(url)
    time.sleep(3) 

    # Lấy phần nội dung chính
    content = driver.find_element(By.CSS_SELECTOR, "#mw-content-text .mw-parser-output")
     # lấy tất cả các bảng chứa danh sách trường
    tables = content.find_elements(By.CSS_SELECTOR, "table.wikitable")

    for table in tables:
        # lấy tất cả hàng trong bảng (tr)
        rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")

        # bỏ hàng đầu tiên (header)
        for row in rows[1:]:
            try:
                # ô đầu tiên của hàng thường là tên trường
                first_td = row.find_element(By.CSS_SELECTOR, "td")
                a = first_td.find_element(By.CSS_SELECTOR, "a")
                href = a.get_attribute("href") or ""

                if href.startswith("https://vi.wikipedia.org/wiki/"):
                    all_links.append(href)

            except:
                pass

except Exception as e:
    print("Error when getting university links:", e)

driver.quit()

print("Số link trường lấy được:", len(all_links))




count = 0

for link in all_links:
    # if count > 4:
    #     break

    count += 1
    print(link)
    try:
        driver = webdriver.Chrome()
        driver.get(link)
        time.sleep(2)

        # ----- Tên trường (heading) -----
        try:
            name = driver.find_element(By.ID, "firstHeading").text
        except:
            try:
                name = driver.find_element(By.TAG_NAME, "h1").text
            except:
                name = ""

        # ----- Ký hiệu / tên viết tắt -----
        try:
            short_name_el = driver.find_element(By.XPATH, "//table[contains(@class,'infobox')]""//tr[th[contains(.,'Viết tắt')] or th[contains(.,'Abbreviation')]]/td")
            short_name = short_name_el.text.strip()
        except:
            short_name = ""

        # ----- Ngày thành lập -----
        try:
            founded_el = driver.find_element(
                By.XPATH,
                "//table[contains(@class,'infobox')]"
                "//tr[th[contains(.,'Thành lập') or contains(.,'Established')]]/td"
            )
            founded = founded_el.text.strip()
        except:
            founded = ""

        # ----- Hiệu trưởng / Giám đốc -----
        try:
            rector_el = driver.find_element(
                By.XPATH,
                "//table[contains(@class,'infobox')]"
                "//tr[th[contains(.,'Hiệu trưởng') or contains(.,'Giám đốc') "
                "or contains(.,'Rector') or contains(.,'President')]]/td"
            )
            rector = rector_el.text.strip()
        except:
            rector = ""

        # ----- Website -----
        try:
            website_el = driver.find_element(
                By.XPATH,
                "//table[contains(@class,'infobox')]"
                "//tr[th[contains(.,'Website')]]//td//a[1]"
            )
            website = website_el.get_attribute("href") or website_el.text.strip()
        except:
            website = ""

        # Tạo dict thông tin trường
        uni = {
            'name': name,
            'short_name': short_name,
            'founded': founded,
            'rector': rector,
            'website': website
        }

        # Convert sang DataFrame 1 dòng
        uni_df = pd.DataFrame([uni])

        # Nối vào DataFrame chính (giống bài painters)
        d = pd.concat([d, uni_df], ignore_index=True)

        driver.quit()

    except Exception as e:
        print("Error when crawling:", link, "-", e)
        try:
            driver.quit()
        except:
            pass

# In kết quả và lưu Excel
print(d)

file_name = "Universities_Vietnam.xlsx"
d.to_excel(file_name, index=False)
print("DataFrame is written to Excel File successfully:", file_name)
