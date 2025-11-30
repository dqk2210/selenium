from pygments.formatters.html import webify
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pandas as pd
import re

all_links = []
driver = webdriver.Chrome()
driver.get("https://gochek.vn/collections/all")
time.sleep(3)

anchors = driver.find_elements(By.CSS_SELECTOR, "a[href*='/products/']")
for a in anchors:
    href = a.get_attribute("href")
    if href and href not in all_links:
        all_links.append(href)

print("Số link sản phẩm:", len(all_links))
driver.quit()


d = pd.DataFrame({'name': [], 'price': [], 'old_price': [], 'sale_percent': [],'stock_status': [], 'video_url': [], 'description': [] })

count = 0
for link in all_links:
    print(link)
    try:
        driver = webdriver.Chrome()
        driver.get(link)
        time.sleep(3)  

        # Tên sản phẩm 
        try:
            name = driver.find_element(By.CSS_SELECTOR, ".product-title h1").text
        except:
            name = ""

        #  Giá hiện tại
        try:
            price = driver.find_element(By.CSS_SELECTOR, ".product-price .pro-price").text
        except:
            price = ""

        # Giá gốc 
        try:
            old_price = driver.find_element(By.CSS_SELECTOR, ".product-price del").text
        except:
            old_price = ""

        #  % khuyến mãi 
        try:
            sale_percent = driver.find_element(By.CSS_SELECTOR, ".product-price .pro-sale").text
        except:
            sale_percent = ""

        # ----- TRẠNG THÁI CÒN/HẾT HÀNG (THEO NÚT BẤM) -----
        try:
            btn = driver.find_element(By.CSS_SELECTOR, "button.add-to-cartProduct")
            btn_text = btn.text.strip().lower()
            if "liên" in btn_text:      # nút "Liên hệ"
                stock_status = "Hết hàng"
            else:                       # nút "Thêm vào giỏ hàng"
                stock_status = "Còn hàng"
        except:
            stock_status = ""

        # Mô tả sản phẩm 
        try:
            desc_element = driver.find_element(By.CSS_SELECTOR, ".description-productdetail")
            description = desc_element.text
        except:
            description = ""

        # Link video hướng dẫn 
        try:
            iframe = driver.find_element(By.CSS_SELECTOR, "#proTabs2 iframe")
            video_url = iframe.get_attribute("data-src") or iframe.get_attribute("src")
        except:
            video_url = ""

        # # ===== Nội dung bảo hành (tab Chính sách bảo hành – proTabs3) =====
        # try:
        #     warranty_element = driver.find_element(By.CSS_SELECTOR, "#proTabs3")
        #     warranty = warranty_element.text
        # except:
        #     warranty = ""

        # Tạo dict thông tin 1 sản phẩm
        product = {'name': name, 'price': price, 'old_price': old_price, 'sale_percent': sale_percent, 'stock_status': stock_status, 'video_url': video_url, 'description': description}

        # Thêm vào DataFrame chính
        d = pd.concat([d, pd.DataFrame([product])], ignore_index=True)

        driver.quit()

    except :
        print("Lỗi khi crawl sản phẩm:")
        try:
            driver.quit()
        except:
            pass

# Lưu
print(d)
file_name = "GoChek.xlsx"
d.to_excel(file_name, index=False)
print("Đã ghi DataFrame vào file Excel:", file_name)