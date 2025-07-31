import pymssql
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


db_settings = {
    "host": "127.0.0.1",
    "user": "",
    "password": "",
    "database": "",
    "charset": "utf8"
}

taiwan50 = []

def find_Taiwan50():
    options = Options()
    options.add_argument("--headless")  # 執行時不顯示瀏覽器
    options.add_argument("--disable-notifications")  # 禁止瀏覽器的彈跳通知
    driver = webdriver.Edge(options=options)
    driver.get("https://www.cmoney.tw/etf/tw/0050/fundholding")
        
    try:
        # 等元件跑完再接下來的動作，避免讀取不到內容
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//table//tbody")))
        tbody_list = driver.find_elements(By.XPATH,"//table//tbody")
        first = True
        for tbody in tbody_list:
            if(first):
                first = False
                continue
            tr_list = tbody.find_elements(By.XPATH, "tr")

        for tr in tr_list:
            td_list = tr.find_elements(By.XPATH, "td")
            taiwan50.append(td_list[0].text)
            
    except TimeoutException as e:
        print(e)    
    driver.close()


def find_stock(url, start, end):
    try:
        conn = pymssql.connect(**db_settings)
        with conn.cursor() as cursor:
            command = "INSERT INTO [dbo].[股票資訊資料表名稱] (stock_code, name, type, category, isTaiwan50) VALUES (%s, %s, %s, %s, %d)"
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")

            # TODO : 練習(這邊有多行程式碼)
            conn.commit()
    except Exception as e:
       print(e)

find_Taiwan50()
find_stock("https://isin.twse.com.tw/isin/C_public.jsp?strMode=4", "股票", "特別股")
find_stock("https://isin.twse.com.tw/isin/C_public.jsp?strMode=2", "股票", "上市認購(售)權證")
