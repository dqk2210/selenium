import sqlite3
from BaiTap01 import *
# 1. Kết nối tới cơ sở dữ liệu
conn = sqlite3.connect("inventory.db")

# Tạo đối tượng 'cursor' để thực thi các câu lệnh SQL
cursor = conn.cursor()

cursor.execute(sql4)