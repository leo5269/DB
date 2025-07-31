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

# 儲存台灣50前10的陣列
taiwan50 = []

def find_Taiwan50():
    options = Options()
    options.add_argument("--headless")  # 執行時不顯示瀏覽器
    options.add_argument("--disable-notifications")  # 禁止瀏覽器的彈跳通知
    driver = webdriver.Edge(options=options)
    driver.get("https://www.cmoney.tw/etf/tw/0050/fundholding")
        
    # TODO : 練習
               
    driver.close()


def find_stock(url, start, end):
    try:
        conn = pymssql.connect(**db_settings)
        # TODO : 練習
    except Exception as e:
       print(e)

find_Taiwan50()
find_stock("https://isin.twse.com.tw/isin/C_public.jsp?strMode=4", "股票", "特別股")
find_stock("https://isin.twse.com.tw/isin/C_public.jsp?strMode=2", "股票", "上市認購(售)權證")
