"""
Đề Bài Thực Hành: Cào Dữ Liệu Long Châu và Quản Lý SQLite
I. Mục Tiêu
    Thực hiện cào dữ liệu sản phẩm từ trang web chính thức của chuỗi nhà thuốc Long Châu bằng công cụ Selenium, lưu trữ dữ liệu thu thập được một cách tức thời vào cơ sở dữ liệu SQLite, và kiểm tra chất lượng dữ liệu.

II. Yêu Cầu Kỹ Thuật (Scraping & Lưu trữ)
    Công cụ: Sử dụng thư viện Selenium kết hợp với Python và Pandas (cho việc quản lý DataFrame tạm thời và lưu vào DB).

    Phạm vi Cào: Chọn một danh mục sản phẩm cụ thể trên trang Long Châu (ví dụ: "Thực phẩm chức năng", "Chăm sóc da", hoặc "Thuốc") và cào ít nhất 50 sản phẩm (có thể cào nhiều trang/URL khác nhau).

    Dữ liệu cần cào: Đối với mỗi sản phẩm, cần thu thập ít nhất các thông tin sau (table phải có các cột bên dưới):

        Mã sản phẩm (id): cố gắng phân tích và lấy mã sản phẩm gốc từ trang web, nếu không được thì dùng mã tự tăng.

        Tên sản phẩm (product_name)

        Giá bán (price)

        Giá gốc/Giá niêm yết (nếu có, original_price)

        Đơn vị tính (ví dụ: Hộp, Chai, Vỉ, unit)

        Link URL sản phẩm (product_url) (Dùng làm định danh duy nhất)

    Lưu trữ Tức thời:

        Sử dụng thư viện sqlite3 để tạo cơ sở dữ liệu (longchau_db.sqlite).

        Thực hiện lưu trữ dữ liệu ngay lập tức sau khi cào xong thông tin của mỗi sản phẩm (sử dụng conn.cursor().execute() hoặc DataFrame.to_sql(if_exists='append')) thay vì lưu trữ toàn bộ sau khi kết thúc quá trình cào.

        Sử dụng product_url hoặc một trường định danh khác làm PRIMARY KEY (hoặc kết hợp với lệnh INSERT OR IGNORE) để tránh ghi đè nếu chạy lại code.

III. Yêu Cầu Phân Tích Dữ Liệu (Query/Truy Vấn)
    Sau khi dữ liệu được thu thập, tạo và thực thi ít nhất 15 câu lệnh SQL (queries) để khảo sát chất lượng và nội dung dữ liệu.

    Nhóm 1: Kiểm Tra Chất Lượng Dữ Liệu (Bắt buộc)
        Kiểm tra trùng lặp (Duplicate Check): Kiểm tra và hiển thị tất cả các bản ghi có sự trùng lặp dựa trên trường product_url hoặc product_name.

        Kiểm tra dữ liệu thiếu (Missing Data): Đếm số lượng sản phẩm không có thông tin Giá bán (price là NULL hoặc 0).

        Kiểm tra giá: Tìm và hiển thị các sản phẩm có Giá bán lớn hơn Giá gốc/Giá niêm yết (logic bất thường).

        Kiểm tra định dạng: Liệt kê các unit (đơn vị tính) duy nhất để kiểm tra sự nhất quán trong dữ liệu.

        Tổng số lượng bản ghi: Đếm tổng số sản phẩm đã được cào.

    Nhóm 2: Khảo sát và Phân Tích (Bổ sung)
        Sản phẩm có giảm giá: Hiển thị 10 sản phẩm có mức giá giảm (chênh lệch giữa original_price và price) lớn nhất.

        Sản phẩm đắt nhất: Tìm và hiển thị sản phẩm có giá bán cao nhất.

        Thống kê theo đơn vị: Đếm số lượng sản phẩm theo từng Đơn vị tính (unit).

        Sản phẩm cụ thể: Tìm kiếm và hiển thị tất cả thông tin của các sản phẩm có tên chứa từ khóa "Vitamin C".

        Lọc theo giá: Liệt kê các sản phẩm có giá bán nằm trong khoảng từ 100.000 VNĐ đến 200.000 VNĐ.

    Nhóm 3: Các Truy vấn Nâng cao (Tùy chọn)
        Sắp xếp: Sắp xếp tất cả sản phẩm theo Giá bán từ thấp đến cao.

        Phần trăm giảm giá: Tính phần trăm giảm giá cho mỗi sản phẩm và hiển thị 5 sản phẩm có phần trăm giảm giá cao nhất (Yêu cầu tính toán trong query hoặc sau khi lấy data).

        Xóa bản ghi trùng lặp: Viết câu lệnh SQL để xóa các bản ghi bị trùng lặp, chỉ giữ lại một bản ghi (sử dụng Subquery hoặc Common Table Expression - CTE).

        Phân tích nhóm giá: Đếm số lượng sản phẩm trong từng nhóm giá (ví dụ: dưới 50k, 50k-100k, trên 100k).

        URL không hợp lệ: Liệt kê các bản ghi mà trường product_url bị NULL hoặc rỗng.
"""

import sqlite3
import time
import pandas as pd
import re
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException
import random

######################################################
## I. Cấu hình và Chuẩn bị
######################################################

# Thiết lập tên file DB và Bảng
GECKO_PATH = r"D:/Khanh/hoc/ma nguon mo/crawl/selenium/project2/geckodriver.exe"
FIREFOX_BINARY_PATH = r"C:/Program Files/Mozilla Firefox/firefox.exe"

DB_FILE = 'LongChau_Data.db'
TABLE_NAME = 'products'
TARGET_URL = 'https://nhathuoclongchau.com.vn/thuoc/thuoc-bo-and-vitamin/thuoc-bo'
max_clicks = 50

options = webdriver.firefox.options.Options();
options.binary_location ="C:/Program Files/Mozilla Firefox/firefox.exe"

# Mở kết nối SQLite và tạo bảng nếu chưa tồn tại
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# tạo bảng
create_table_sql = f"""
CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
    product_url TEXT PRIMARY KEY,
    product_id TEXT,
    product_name TEXT,
    price TEXT,
    original_price TEXT,
    unit TEXT,
    image_url TEXT,
    crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""
cursor.execute(create_table_sql)
conn.commit()
print(f"--- Đã khởi tạo Database: {DB_FILE} ---")

######################################################
## GIAI ĐOẠN 1: LẤY DANH SÁCH LINK
######################################################

links = []
driver = None

try:
    # KHOI TAO FIREFOX
    ser = Service(GECKO_PATH)
    options = webdriver.FirefoxOptions()
    options.binary_location = FIREFOX_BINARY_PATH
    options.headless = False # Quan sat qua trinh crawl
    driver = webdriver.Firefox(options=options, service=ser)


    print(f"\n--- Giai doan 1: lay link tu {TARGET_URL} ---")
    driver.get(TARGET_URL)
    time.sleep(3)

    click_count = 0
    while click_count < max_clicks:
        try:
            # --- CẬP NHẬT QUAN TRỌNG: XPath cho nút Xem thêm ---
            # Tìm thẻ button mà bên trong có thẻ span chứa chữ "Xem thêm"
            xpath_button = "//button[.//span[contains(text(), 'Xem thêm')]]"
            
            load_more_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, xpath_button))
            )

            # Scroll tới nút để tránh bị thanh menu che khuất
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", load_more_btn)
            time.sleep(1) # Đợi 1 chút sau khi scroll
            load_more_btn.click()

            print(f"da click 'Xem them' lan thu {click_count +1}")
            click_count += 1
            time.sleep(5) 

        except (TimeoutException, NoSuchElementException):
            print(" khong tim thay nut xem them hoac da het san pham")
            break
        except ElementClickInterceptedException:
            print("Nut bi che, thu scroll them 200px...")
            driver.execute_script("window.scrollBy(0, 200);")
            time.sleep(2)
        except:
            print(f"Lỗi khác khi click")
            break

    #2. Lấy tất cả thẻ <a> trỏ tới sản phẩm
    print("dang quet link san pham tren trang...")
    
    try:
        elements = driver.find_elements(By.XPATH, "//a[contains(@href, '.html')]")
        for el in elements:
            href = el.get_attribute('href')
            if href and "nhathuoclongchau.com.vn" in href: 
                if href not in links:
                    links.append(href)
    except:
         print(f"Loi khi lay link")
         
    print(f"--> Tim thay tong cong {len(links)} link san pham")
    driver.quit()

except:
    print(f"Lỗi khởi tạo driver hoặc lấy link")
    if driver: driver.quit()

######################################################
## IV. GIAI ĐOẠN 2: CÀO CHI TIẾT & LƯU DB
######################################################

# lay danh sach link co trong db de bo qua
cursor.execute(f"SELECT product_url FROM {TABLE_NAME}")
existing_links = set(row[0] for row in cursor.fetchall())
print(f"Da co {len(existing_links)}")

# Khởi tạo lại driver cho giai đoạn 2
try:
    ser = Service(GECKO_PATH)
    options = webdriver.FirefoxOptions()

    options.binary_location = FIREFOX_BINARY_PATH

    options.headless = False
    driver = webdriver.Firefox(options=options, service=ser)

    count = 0 
    for link in links:
        if link in existing_links:
            continue
        print(f"Dang xu ly ({count+1}: {link})")

        try:
            driver.get(link)
            time.sleep(3)

            product_name = ""
            price = ""
            original_price = ""
            unit = ""
            image_url = ""
            
            # lay id san pham o cuoi url
            match = re.search(r'(\d+)\.html', link)
            if match:
                product_id = match.group(1)
            else:
                product_id = ""

            #lay ten san pham
            try:
            
                product_name = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, "h1"))).text
            except:
                pass
            
            #lay gia ban
            try:
                price_el = driver.find_element(By.CSS_SELECTOR, "[data-test='price']") 
                price = price_el.text.replace("đ", "").replace(".", "").strip()
            except:
                price = "Liên hệ"
            
            #lay gia goc
            try:
                orig_price_el = driver.find_element(By.CSS_SELECTOR, "[data-test='strike_price']")
                original_price = orig_price_el.text.replace("đ", "").replace(".", "").strip()
            except:
                original_price = "" 

            
            #Donn vi tinh
            try:
                unit_el = driver.find_element(By.CSS_SELECTOR, "[data-test='unit']")
                unit = unit_el.text.strip()
            except:
                # Backup: Thử cắt chuỗi từ tên nếu không tìm thấy
                if "/" in product_name:
                    unit = product_name.split("/")[-1].strip()
                else:
                    unit = ""
            
            # 5. hinh anh 
            try:
                img_el = driver.find_element(By.CSS_SELECTOR, "img.gallery-img")
                image_url = img_el.get_attribute("src")
            except:
                image_url = ""
            
            #Luu vao DB ngay lap tuc
            sql = f"""
            INSERT OR REPLACE INTO {TABLE_NAME} (product_url, product_id, product_name, price, original_price, unit, image_url)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """

            cursor.execute(sql, (link, product_id, product_name, price, original_price, unit, image_url))
            conn.commit()

            print(f"  --> Da luu: {product_name} | Gia: {price}")
            count +=1

        except Exception as e:
            print(f" --> loi khi cao {link}: {e}")
        
        time.sleep(3)
    
    driver.quit()

except Exception as e:
    print(f"Lỗi khởi tạo driver đợt 2: {e}")
print("\nHoàn tất quá trình cào và lưu dữ liệu tức thời.")


    #Nhóm 1: Kiểm Tra Chất Lượng Dữ Liệu (Bắt buộc)
    #     Kiểm tra trùng lặp (Duplicate Check): Kiểm tra và hiển thị tất cả các bản ghi có sự trùng lặp dựa trên trường product_url hoặc product_name.
q1 = """select products_name, count(*) as SOLAN from products group by product_name having SOLAN > 1"""
    #     Kiểm tra dữ liệu thiếu (Missing Data): Đếm số lượng sản phẩm không có thông tin Giá bán (price là NULL hoặc 0).
q2 = """select count(*) as soluong from products where price is null or price = '' or price = 'Liên hệ' """
    #     Kiểm tra giá: Tìm và hiển thị các sản phẩm có Giá bán lớn hơn Giá gốc/Giá niêm yết (logic bất thường).
q3 = """select products_name, price, original_price from products where original_price !='' and cast(price as integer) > cast(original_price as integer) """
    #     Kiểm tra định dạng: Liệt kê các unit (đơn vị tính) duy nhất để kiểm tra sự nhất quán trong dữ liệu.
q4 = """select distinct unit from products"""
    #     Tổng số lượng bản ghi: Đếm tổng số sản phẩm đã được cào.
q5 = """select count(*) as tong from products"""
    # Nhóm 2: Khảo sát và Phân Tích (Bổ sung)
    #     Sản phẩm có giảm giá: Hiển thị 10 sản phẩm có mức giá giảm (chênh lệch giữa original_price và price) lớn nhất.
q6 = """select product_name,price,original_price,(cast(original_price as integer)- cast(price as integer)) as chenhlech
        from products
        where original_price != ''
        order by chenhlech desc
        limit 10 """
    #     Sản phẩm đắt nhất: Tìm và hiển thị sản phẩm có giá bán cao nhất.
q7 = """select * from products where cast(price as integer) = (select max(cast(price as integer)) from products)"""
    #     Thống kê theo đơn vị: Đếm số lượng sản phẩm theo từng Đơn vị tính (unit).
q8 = """select unit, count(*) as num from products group by unit order by num desc"""
    #     Sản phẩm cụ thể: Tìm kiếm và hiển thị tất cả thông tin của các sản phẩm có tên chứa từ khóa "Vitamin C".
q9 = """select * from products where product_name like '%Vitamin C%'"""
    #     Lọc theo giá: Liệt kê các sản phẩm có giá bán nằm trong khoảng từ 100.000 VNĐ đến 200.000 VNĐ.
q10 = """select product_name, price from products where cast(price as integer) between 100000 and 200000 """
    # Nhóm 3: Các Truy vấn Nâng cao (Tùy chọn)
    #     Sắp xếp: Sắp xếp tất cả sản phẩm theo Giá bán từ thấp đến cao.
q11 = """select product_name, price from products order by cast(price as integer) asc"""
    #     Phần trăm giảm giá: Tính phần trăm giảm giá cho mỗi sản phẩm và hiển thị 5 sản phẩm có phần trăm giảm giá cao nhất (Yêu cầu tính toán trong query hoặc sau khi lấy data).
q12 = """select product_name, price, original_price, round(((cast(original_price as float)-cast(price as float)) / cast(original_price as float)) *100, 2) as phantram
         from products
         where original_price != '' and original_price != '0'
         order by phantram desc
         limit 5"""
    #     Xóa bản ghi trùng lặp: Viết câu lệnh SQL để xóa các bản ghi bị trùng lặp, chỉ giữ lại một bản ghi (sử dụng Subquery hoặc Common Table Expression - CTE).
q13 = """delete from products where rowid not in(select min(row) from products group by product_name)"""
    #     Phân tích nhóm giá: Đếm số lượng sản phẩm trong từng nhóm giá (ví dụ: dưới 50k, 50k-100k, trên 100k).
q14 = """select
            case when cast(price as integer) < 50000 then 'duoi 50k'
                when cast(price as integer) between 50000 and 100000 then '50k - 100k'
                else 'tren 100k'
            end as nhom,
            count(*) as num
        from products
        group by nhom
        """
    #     URL không hợp lệ: Liệt kê các bản ghi mà trường product_url bị NULL hoặc rỗng.
q15 = """select* from products where product_url is null or product_url = ''"""
cursor.execute(q1)
conn.commit()

# Dong ket noi 
conn.close()
print("\nĐã đóng kết nối cơ sở dữ liệu.")



     
        



