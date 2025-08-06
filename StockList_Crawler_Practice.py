import pymssql
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.edge.service import Service


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
    options.add_argument("start-maximized")
    
    service = Service(executable_path="msedgedriver.exe")
    driver = webdriver.Edge(service=service, options=options)
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
            command = "INSERT INTO [dbo].[你的股票資訊資料表名稱] (stock_code, name, type, category, isTaiwan50) VALUES (%s, %s, %s, %s, %d)"
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")

            result = soup.select("table td b")
            for tr in result: # 在所有的粗體標籤中找到我們需要的
                if(tr.text.strip() == start):
                    start_td = tr.find_parent("tr")
                elif(tr.text.strip() == end):
                    end_td = tr.find_parent("tr")

            list_td = start_td.find_next("tr") # 找出下一個tr標籤
            while(list_td != end_td):
                child_list = list_td.find_all('td') # 列出tr標籤中的所有td標籤
                stock_id, stock_name = child_list[0].text.split("　")
                cursor.execute(command, (stock_id, stock_name, child_list[3].text, child_list[4].text, (stock_id in taiwan50)))
                list_td = list_td.find_next("tr")
            conn.commit()
    except Exception as e:
       print(e)

find_Taiwan50()
find_stock("https://isin.twse.com.tw/isin/C_public.jsp?strMode=4", "股票", "特別股")
find_stock("https://isin.twse.com.tw/isin/C_public.jsp?strMode=2", "股票", "上市認購(售)權證")
