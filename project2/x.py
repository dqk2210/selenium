from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
import time
import pandas as pd
import random
import re

# ================== CẤU HÌNH NGƯỜI DÙNG (SỬA Ở ĐÂY) ==================
# HÃY THAY DÒNG DƯỚI BẰNG AUTH_TOKEN MỚI CỦA BẠN LẤY TỪ F12
MY_AUTH_TOKEN = "e87..................." 

# Đường dẫn đến geckodriver và firefox (Sửa lại cho đúng máy bạn)
GECKO_PATH = r"D:/Khanh/hoc/ma nguon mo/crawl/selenium/project2/geckodriver.exe"
FIREFOX_BINARY_PATH = "C:/Program Files/Mozilla Firefox/firefox.exe"

# ================== KHỞI TẠO DRIVER ==================
ser = Service(GECKO_PATH)
options = webdriver.firefox.options.Options()
options.binary_location = FIREFOX_BINARY_PATH

# Các thiết lập để ẩn danh tính bot cơ bản
options.set_preference("dom.webdriver.enabled", False)
options.set_preference("useAutomationExtension", False)

driver = webdriver.Firefox(options=options, service=ser)
wait = WebDriverWait(driver, 15) # Thời gian chờ tối đa 15s

def parse_metric(text):
    """Làm sạch số liệu (VD: '5.5K' -> '5.5K', '' -> '0')"""
    if not text: return "0"
    return text.replace('\n', '').strip()

try:
    # 1. Truy cập trang chủ lần đầu để tạo session
    print("Truy cập trang x.com...")
    driver.get("https://x.com")
    time.sleep(2)

    # 2. TIÊM COOKIE (BƯỚC QUAN TRỌNG NHẤT)
    print(f"Đang tiêm auth_token: {MY_AUTH_TOKEN[:10]}...")
    driver.add_cookie({
        'name': 'auth_token',
        'value': "1bbdd10ec369c566c080f88b0449a1131c8be012",
        'domain': '.x.com',
        'path': '/',
        'secure': True,
        'httpOnly': True
    })

    # 3. Tải lại trang để áp dụng Cookie
    print("Đã thêm Cookie. Đang tải lại trang...")
    driver.refresh()
    
    # 4. Chờ xem đăng nhập thành công không
    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'article[data-testid="tweet"]')))
        print(">>> ĐĂNG NHẬP THÀNH CÔNG! Bắt đầu cào dữ liệu chi tiết...")
    except TimeoutException:
        print("!!! LỖI: Không thấy bài viết nào. Có thể Token đã hết hạn hoặc sai.")
        driver.quit()
        exit()

    # ================== CRAWL DỮ LIỆU CHI TIẾT ==================
    tweets_data = []
    seen_ids = set() # Dùng Tweet ID để lọc trùng chính xác hơn
    max_tweets = 10       
    scroll_attempts = 0   
    max_scroll_attempts = 15 

    while len(tweets_data) < max_tweets and scroll_attempts < max_scroll_attempts:
        try:
            articles = driver.find_elements(By.CSS_SELECTOR, 'article[data-testid="tweet"]')
            
            for tweet in articles:
                if len(tweets_data) >= max_tweets:
                    break
                    
                try:
                    # --- 1. Lấy Tweet ID, URL và Thời gian ---
                    try:
                        time_element = tweet.find_element(By.TAG_NAME, "time")
                        posted_time = time_element.get_attribute("datetime")
                        # Thẻ cha của <time> thường là thẻ <a> chứa link tweet
                        link_element = time_element.find_element(By.XPATH, "./..")
                        tweet_url = link_element.get_attribute("href")
                        tweet_id = tweet_url.split("/")[-1]
                    except:
                        # Nếu không lấy được ID thì bỏ qua tweet này (thường là quảng cáo)
                        continue

                    if tweet_id in seen_ids:
                        continue

                    # --- 2. Lấy User Info ---
                    try:
                        # Tìm phần tử chứa tên user
                        user_block = tweet.find_element(By.CSS_SELECTOR, 'div[data-testid="User-Name"]')
                        user_text = user_block.text.split("\n")
                        
                        name = user_text[0]
                        username = ""
                        for line in user_text:
                            if line.startswith("@"):
                                username = line
                                break
                        
                        # Avatar
                        try:
                            avatar_elem = tweet.find_element(By.CSS_SELECTOR, 'div[data-testid="Tweet-User-Avatar"] img')
                            profile_picture = avatar_elem.get_attribute("src")
                        except:
                            profile_picture = ""
                            
                    except Exception as e:
                        name = "Unknown"
                        username = "Unknown"
                        profile_picture = ""

                    # --- 3. Lấy Nội dung (Content) ---
                    try:
                        content = tweet.find_element(By.CSS_SELECTOR, 'div[data-testid="tweetText"]').text
                    except:
                        content = ""

                    # --- 4. Lấy Metrics (Reply, Retweet, Like, View) DỰA VÀO VỊ TRÍ ---
                    # Logic mới: Tìm nhóm nút hành động (role="group") và lấy theo thứ tự
                    replies, retweets, likes, views = "0", "0", "0", "0"
                    
                    try:
                        # Tìm nhóm các nút (Reply, Retweet, Like, View, Share)
                        group = tweet.find_element(By.CSS_SELECTOR, 'div[role="group"]')
                        
                        # Lấy tất cả các thẻ div con trực tiếp của group
                        # Mỗi thẻ div này tương ứng với 1 nút
                        buttons = group.find_elements(By.XPATH, "./div")
                        
                        # Hàm lấy text bên trong nút (sử dụng innerText để lấy cả text ẩn nếu có)
                        def get_btn_text(btn):
                            txt = btn.get_attribute("innerText") or btn.text
                            # Lọc chỉ lấy phần số (VD: "542" hoặc "1.2K")
                            # Regex tìm chuỗi số có thể kèm K/M/B
                            match = re.search(r'(\d+(?:\.\d+)?[KMB]?)', txt)
                            return match.group(0) if match else "0"

                        if len(buttons) >= 4:
                            replies = get_btn_text(buttons[0]) # Nút 1: Reply
                            retweets = get_btn_text(buttons[1]) # Nút 2: Retweet
                            likes = get_btn_text(buttons[2])    # Nút 3: Like
                            views = get_btn_text(buttons[3])    # Nút 4: View
                        elif len(buttons) == 3: 
                            # Trường hợp hiếm: ko có nút View?
                            replies = get_btn_text(buttons[0])
                            retweets = get_btn_text(buttons[1])
                            likes = get_btn_text(buttons[2])
                            
                    except Exception as e:
                        # print(f"Lỗi lấy metrics: {e}")
                        pass

                    # --- 5. Lưu dữ liệu ---
                    item = {
                        "tweet_id": tweet_id,
                        "username": username,
                        "name": name,
                        "replies": replies,
                        "retweets": retweets,
                        "likes": likes,
                        "views": views,
                        "posted_time": posted_time,
                        "content": content,
                        "tweet_url": tweet_url,
                        "profile_picture": profile_picture
                    }
                    
                    tweets_data.append(item)
                    seen_ids.add(tweet_id)
                    print(f"[{len(tweets_data)}/{max_tweets}] {username}: {content[:20]}... | R:{replies} RT:{retweets} L:{likes} V:{views}")

                except StaleElementReferenceException:
                    continue
                except Exception as e:
                    continue

            if len(tweets_data) >= max_tweets:
                print(">>> Đã lấy đủ số lượng yêu cầu.")
                break

            # -- SCROLL --
            print(f"Đang cuộn trang lần {scroll_attempts + 1}...")
            driver.execute_script("window.scrollBy(0, window.innerHeight);")
            time.sleep(random.uniform(3, 6)) 
            scroll_attempts += 1

        except Exception as e:
            print(f"Có lỗi trong quá trình scroll: {e}")
            break

    # ================== KẾT THÚC ==================
    print(f"\nTổng kết: Lấy được {len(tweets_data)} tweets")

    if len(tweets_data) > 0:
        df = pd.DataFrame(tweets_data)
        # Hiển thị thông tin cơ bản
        print(df[['username', 'likes', 'views', 'content']].head())
        
        filename = "tweets_full_info.csv"
        df.to_csv(filename, index=False, encoding="utf-8-sig")
        print(f"Đã lưu dữ liệu đầy đủ vào file: {filename}")
    else:
        print("Không lấy được dữ liệu nào.")

except Exception as e:
    print(f"Lỗi chương trình: {e}")

finally:
    # driver.quit()
    pass