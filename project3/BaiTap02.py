import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd
import re
import os # Thêm thư viện để kiểm tra/xóa file DB (tùy chọn)

######################################################
## I. Cấu hình và Chuẩn bị
######################################################

# Thiết lập tên file DB và Bảng
DB_FILE = 'Painters_Data.db'
TABLE_NAME = 'painters_info'
all_links = []
all_nationalities = []
all_births_backup = []
all_deaths_backup = []
# Tùy chọn cho Chrome (có thể chạy ẩn nếu cần, nhưng để dễ debug thì không dùng)
chrome_options = Options()
chrome_options.add_argument("--headless") 

# Nếu muốn bắt đầu với DB trống, có thể xóa file cũ (Tùy chọn)
if os.path.exists(DB_FILE):
    os.remove(DB_FILE)
    print(f"Đã xóa file DB cũ: {DB_FILE}")

# Mở kết nối SQLite và tạo bảng nếu chưa tồn tại
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Tạo bảng
create_table_sql = f"""
CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
    name TEXT PRIMARY KEY, -- Sử dụng tên làm khóa chính để tránh trùng lặp
    birth TEXT,
    death TEXT,
    nationality TEXT
)
"""
cursor.execute(create_table_sql)
conn.commit()
print(f"Đã kết nối và chuẩn bị bảng '{TABLE_NAME}' trong '{DB_FILE}'.")

# Hàm đóng driver an toàn
def safe_quit_driver(driver):
    try:
        if driver:
            driver.quit()
    except:
        pass

def extract_dates_from_text(text):
    # Tìm kiếm mẫu: (Năm - Năm)
    # Hỗ trợ cả dấu gạch ngang (-) và gạch dài (–), có thể có khoảng trắng
    match = re.search(r'\((\d{3,4})[\s–-]+(\d{3,4})\)', text)
    if match:
        return match.group(1), match.group(2) # Trả về (birth, death)
    
    # Trường hợp chỉ có năm sinh: (b. 1888)
    match_born = re.search(r'\(\s*b\.?\s*(\d{3,4})', text)
    if match_born:
        return match_born.group(1), ""
        
    return "", ""

def extract_nationality(li_text: str) -> str:
    # 1. Cắt bỏ phần sau dấu ) (sau tên + năm sinh/tử)
    parts = li_text.rsplit(')', 1)
    if len(parts) == 2:
        tail = parts[1].strip()
    else:
        # Nếu không có năm sinh/tử (không có dấu ')'), sử dụng toàn bộ chuỗi
        tail = li_text
        
    # Chuẩn hóa để dễ làm việc (ví dụ: loại bỏ dấu phẩy đầu)
    tail = tail.strip(' ,.;').replace('–', '-')

    # 2. Loại bỏ các từ chỉ nghề nghiệp, thể loại, hoặc mô tả không phải quốc tịch
    keywords_to_remove = [
        r'\b(painter|artist|sculptor|printmaker|illustrator|ceramicist|muralist|miniaturist|portraitist|landscape|designer|weaver|photographer)\b',
        r'\b(portrait|still life|abstract|folk|watercolour|watercolor|oil|tapestry|religious|genre|history|marine|animal|romantic|modern)\b',
        r'\b(golden age|baroque|renaissance|impressionist|expressionist|surrealist|cubist|realist|futurist|still-life|teacher|battle-scene|lithographer|art director|graphic|etcher)\b',
        r'and' # Để xử lý trường hợp 'Scottish linocut and woodcut'
    ]

    # 3. Thực hiện loại bỏ tuần tự
    for pattern in keywords_to_remove:
        # Thay thế từ khóa bằng khoảng trắng, sau đó làm sạch khoảng trắng thừa
        tail = re.sub(pattern, ' ', tail, flags=re.IGNORECASE).strip()

    # 4. Lấy phần đầu tiên (thường là Quốc tịch) trước dấu phẩy hoặc dấu chấm sau khi làm sạch
    # Ví dụ: 'Dutch Golden Age' -> 'Dutch'
    result = re.split(r'[,\.]\s*', tail, maxsplit=1)[0]
    
    # Loại bỏ các từ còn sót lại không phải quốc tịch (ví dụ: 'of')
    result = result.replace('of', '').strip()
    
    # Xử lý trường hợp 'English wartime' -> 'English'
    result = re.sub(r'\b(wartime|linocut|woodcut|designer)\b', '', result, flags=re.IGNORECASE).strip()
    
    # Làm sạch lần cuối
    return result.strip(' ,.;-')


######################################################
## II. Lấy Đường dẫn (URLs)
######################################################

print("\n--- Bắt đầu Lấy Đường dẫn ---")

# Lặp qua ký tự 'F' (chr(70))
for i in range(70, 71): 
    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options) # Khởi tạo driver cho phần này
        url = "https://en.wikipedia.org/wiki/List_of_painters_by_name_beginning_with_%22"+chr(i)+"%22"
        driver.get(url)
        time.sleep(3)

        # Lấy tất cả thẻ ul
        ul_tags = driver.find_elements(By.TAG_NAME, "ul")
        
        # Thử chọn chỉ mục (index) 20. Cần kiểm tra lại nếu index này thay đổi.
        if len(ul_tags) > 20:
            ul_painters = ul_tags[19] 
            li_tags = ul_painters.find_elements(By.TAG_NAME, "li")

            # Lọc các đường dẫn hợp lệ (có thuộc tính href)
            for tag in li_tags:
                try:
                    a_tag = tag.find_element(By.TAG_NAME, "a")
                    link = a_tag.get_attribute("href")
                    li_text = tag.text
                    nationality = extract_nationality(li_text)

                    # 2. Lấy ngày sinh/mất dự phòng từ dòng chữ
                    b_backup, d_backup = extract_dates_from_text(li_text)
                    all_links.append(link)  
                    all_nationalities.append(nationality)  
                    all_births_backup.append(b_backup) 
                    all_deaths_backup.append(d_backup)
                except:
                    pass
        else:
            print(f"Lỗi: Không tìm thấy thẻ ul ở chỉ mục 20 cho ký tự {chr(i)}.")

    except Exception as e:
        print(f"Lỗi khi lấy links cho ký tự {chr(i)}: {e}")
    finally:
        safe_quit_driver(driver) # Đóng driver sau khi xong phần này

print(f"Hoàn tất lấy đường dẫn. Tổng cộng {len(all_links)} links đã tìm thấy.")

######################################################
## III. Lấy thông tin & LƯU TRỮ TỨC THỜI
######################################################

print("\n--- Bắt đầu Cào và Lưu Trữ Tức thời ---")
# cursor.execute(f"SELECT link FROM {TABLE_NAME}")
# # Tạo một set (tập hợp) chứa các link đã xong để tra cứu cho nhanh
# existing_links = set(row[0] for row in cursor.fetchall())
# print(f"Đã tìm thấy {len(existing_links)} họa sĩ đã có trong DB. Sẽ bỏ qua các link này.")
count = 0
idx = 0 
for link in all_links:

    # # # Giới hạn số lượng truy cập để thử nghiệm nhanh
    # if (count >= 5): # Đã tăng lên 5 họa sĩ để có thêm dữ liệu mẫu
    #     break
    # count = count + 1

    #Néu không có thì bắt đầu cào 
    backup_birth = all_births_backup[idx]
    backup_death = all_deaths_backup[idx]
    nationality = all_nationalities[idx]
    idx += 1
    print(link, " | ", nationality)

    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options) 
        driver.get(link)
        time.sleep(2)

        # 1. Lấy tên họa sĩ
        try:
            name = driver.find_element(By.TAG_NAME, "h1").text
        except:
            name = ""
        
        try:
            birth_element = driver.find_element(By.XPATH, "//th[text()='Born']/following-sibling::td")
            birth_text = birth_element.text
            # Regex Cải tiến: Tìm bất kỳ năm nào (4 chữ số) HOẶC định dạng ngày đầy đủ, kể cả các dạng như 'c. 1850'
            date_regex = r'\b(c\.\s*\d{4}|\d{1,2}\s+[A-Za-z]+\s+\d{4}|[A-Za-z]+\s+\d{4}|\d{4})\b'
            birth_match = re.search(date_regex, birth_text)
            
            birth = birth_match.group(0) if birth_match else ""
            # Loại bỏ các tham chiếu [1], [a]
            birth = re.sub(r'\[.*?\]', '', birth).strip()
            
        except:
            birth = ""
        if birth == "":
            birth = backup_birth    
        # 3. Lấy ngày mất (Died)
        try:
            death_element = driver.find_element(By.XPATH, "//th[text()='Died']/following-sibling::td")
            death_text = death_element.text
            # Sử dụng Regex Cải tiến tương tự
            date_regex = r'\b(c\.\s*\d{4}|\d{1,2}\s+[A-Za-z]+\s+\d{4}|[A-Za-z]+\s+\d{4}|\d{4})\b'
            death_match = re.search(date_regex, death_text)
            
            death = death_match.group(0) if death_match else ""
            # Loại bỏ các tham chiếu [1], [a]
            death = re.sub(r'\[.*?\]', '', death).strip()
            
        except:
            death = ""
        if death == "":
            death = backup_death
            
        # 4. Lấy quốc tịch (Nationality)
        # try:
        #     nationality_element = driver.find_element(By.CSS_SELECTOR, "table.infobox .birthplace")
        #     nationality = nationality_element.text.strip(":")
        # except:
        #     nationality = ""

        safe_quit_driver(driver)
        
        # 5. LƯU TỨC THỜI VÀO SQLITE
        insert_sql = f"""
        INSERT OR IGNORE INTO {TABLE_NAME} (name, birth, death, nationality) 
        VALUES (?, ?, ?, ?)
        """
        # Sử dụng 'INSERT OR IGNORE' để bỏ qua nếu Tên (PRIMARY KEY) đã tồn tại
        cursor.execute(insert_sql, (name, birth, death, nationality))
        conn.commit()
        print(f"  --> Đã lưu thành công: {name}")
        # # cập nhập vào set existing_links nếu link all_links bị trùng
        # existing_links.add(link)

    except Exception as e:
        print(f"Lỗi khi xử lý hoặc lưu họa sĩ {link}: {e}")
        safe_quit_driver(driver)
        
print("\nHoàn tất quá trình cào và lưu dữ liệu tức thời.")

######################################################
## IV. Truy vấn SQL Mẫu và Đóng kết nối
######################################################

"""
A. Yêu Cầu Thống Kê và Toàn Cục

1. Đếm tổng số họa sĩ đã được lưu trữ trong bảng.
SELECT * FROM painters_info
2. Hiển thị 5 dòng dữ liệu đầu tiên để kiểm tra cấu trúc và nội dung bảng.
SELECT * FROM painters_info LIMIT 5
3. Liệt kê danh sách các quốc tịch duy nhất có trong tập dữ liệu.
SELECT DISTINCT nationality FROM painters_info

B. Yêu Cầu Lọc và Tìm Kiếm

4. Tìm và hiển thị tên của các họa sĩ có tên bắt đầu bằng ký tự 'F'.
SELECT name FROM painters_info WHERE name like "F%"
5. Tìm và hiển thị tên và quốc tịch của những họa sĩ có quốc tịch chứa từ khóa 'French' (ví dụ: French, French-American).
SELECT name nationality FROM painters_info WHERE nationality like "%French%
6. Hiển thị tên của các họa sĩ không có thông tin quốc tịch (hoặc để trống, hoặc NULL).
SELECT name FROM painters_info WHERE nationality IS NULL or nationality =''
7. Tìm và hiển thị tên của những họa sĩ có cả thông tin ngày sinh và ngày mất (không rỗng).
SELECT name, birth, death 
FROM painters_info 
WHERE birth IS NOT NULL AND birth != '' 
  AND death IS NOT NULL AND death != ''

8. Hiển thị tất cả thông tin của họa sĩ có tên chứa từ khóa '%Fales%' (ví dụ: George Fales Baker).
SELECT * FROM painters_info WHERE name LIKE '%Fales%'
C. Yêu Cầu Nhóm và Sắp Xếp

9. Sắp xếp và hiển thị tên của tất cả họa sĩ theo thứ tự bảng chữ cái (A-Z).
SELECT * FROM painters_info ORDER BY name ASC
10. Nhóm và đếm số lượng họa sĩ theo từng quốc tịch.
SELECT nationality, COUNT (*) as num 
FROM painters_info
GROUP BY nationality
ORDER BY num DESC

"""

# Đóng kết nối cuối cùng
conn.close()
print("\nĐã đóng kết nối cơ sở dữ liệu.")