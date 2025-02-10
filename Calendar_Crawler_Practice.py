import calendar
import pymssql
import time
import re
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException

# 🟢 設定要爬取的年份
target_year = 1234  # 你可以手動修改這個值來爬取不同年份

# SQL Server 連線資訊
db_settings = {
    "host": "127.0.0.1",
    "user": "",
    "password": "",
    "database": "",
    "charset": "utf8"
}

# 初始化特殊節日字典
holiday_dir = {}
spring_festival_dates = []  # 用於存儲當年的 3 個「農曆春節前最後交易日」

# 🕵️‍♂️ **爬取 TWSE 休市日**
def crawler():
    options = Options()
    options.add_argument("--headless")  # 不顯示瀏覽器
    options.add_argument("--disable-notifications")  # 禁止通知
    driver = webdriver.Edge(options=options)

    # 進入台灣證券交易所開休市日頁面
    url = "https://www.twse.com.tw/zh/trading/holiday.html"
    driver.get(url)

    try:
        # **等待年份選擇器加載**
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "yy"))
        )

        # **選擇年份**
        select_element = driver.find_element(By.NAME, "yy")  # 找到年份下拉選單
        select = Select(select_element)  # 轉換成 Select 物件
        taiwan_year = str(target_year - 1911)  # 轉換成民國年
        select.select_by_visible_text(f"民國 {taiwan_year} 年")  # 選擇年份

        time.sleep(1)  # 等待下拉選單更新

        # **點擊查詢按鈕**
        search_button = driver.find_element(By.XPATH, "//button[contains(text(),'查詢')]")
        search_button.click()

        # **等待表格載入**
        # TODO : 練習1
        # **抓取所有行**
        # TODO : 練習1

        last_holiday_name = ""  # 記錄最後一個非空的休市名稱
        for holiday in holiday_list:
            try:
                # **取得 月日（星期） 和 休市名稱**
                # TODO : 練習1

                # **如果 holiday_name 為空，則繼承上一個有效的休市名稱**
                if holiday_name:
                    last_holiday_name = holiday_name
                else:
                    holiday_name = last_holiday_name  # 繼承上一次的名稱

                # **使用正則表達式解析日期**
                match = re.search(r"(\d{1,2})月(\d{1,2})日", date_str)
                if not match:
                    print(f"❌ 無法解析日期格式: {date_str}")
                    continue

                month, day = map(int, match.groups())

                # **補上 target_year**
                date_formatted = f"{target_year}{month:02d}{day:02d}"  # YYYYMMDD格式

                # **處理農曆春節前最後交易日**
                if "農曆春節前最後交易日" in holiday_name:
                    spring_festival_dates.append(date_formatted)  # 存入特定的春節前交易日

                # **存入字典**
                holiday_dir[date_formatted] = holiday_name
                print(f"📅 日期: {date_formatted}, other: {holiday_name}")  # 🛠️ Debug用

            except Exception as e:
                print(f"❌ 抓取錯誤: {e}")

    except TimeoutException as e:
        print(f"⚠️ 網頁載入超時: {e}")

    driver.quit()  # **關閉瀏覽器**

    # **寫入資料庫**
    insert_to_db()

# 📌 **將爬取的數據存入 SQL Server**
def insert_to_db():
    work_count = 0

    try:
        conn = pymssql.connect(**db_settings)
        cursor = conn.cursor()

        # **刪除指定年份的舊資料，避免重複寫入**
        delete_query = f"DELETE FROM dbo.calendar WHERE YEAR(date) = {target_year}"
        cursor.execute(delete_query)
        conn.commit()

        # TODO : 練習1 (Hint:插入資料庫會用到的SQL語句，然後assign給insert_query)

        # **處理該年的所有日期**
        for month in range(1, 13):
            for date in range(1, calendar.monthrange(target_year, month)[1] + 1):
                date_str = f"{target_year}{month:02d}{date:02d}"  # YYYYMMDD格式
                weekday = calendar.weekday(target_year, month, date)  # 取得星期 (星期一 = 0)

                # **休市日處理**
                if date_str in holiday_dir:
                    if "國曆新年開始交易日" in holiday_dir[date_str] or "農曆春節後開始交易日" in holiday_dir[date_str]:
                        work_count += 1
                        cursor.execute(insert_query, (date_str, work_count, holiday_dir[date_str]))
                    elif date_str in spring_festival_dates:
                        if date_str == spring_festival_dates[0]:
                            work_count += 1
                            cursor.execute(insert_query, (date_str, work_count, holiday_dir[date_str]))
                        else:
                            cursor.execute(insert_query, (date_str, -1, holiday_dir[date_str]))
                    else:
                        cursor.execute(insert_query, (date_str, -1, holiday_dir[date_str]))
                elif weekday == 5 or weekday == 6:  # **週六、週日**
                    cursor.execute(insert_query, (date_str, -1, ""))
                else:
                    work_count += 1
                    cursor.execute(insert_query, (date_str, work_count, ""))

                conn.commit()

        print(f"✅ {target_year} 年數據成功存入 SQL Server！")
        print(f"🔍 {target_year} 年總交易日數: {work_count}")

    except Exception as e:
        print(f"❌ 寫入資料庫錯誤: {e}")

    finally:
        conn.close()


# 🚀 **執行爬蟲**
crawler()
