from bs4 import BeautifulSoup
import requests
url= "https://www.ptt.cc/bbs/Steam/index.html"

response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

# 找到所有<div class="r-ent">的物件
all_article = soup.select("div[class=r-ent]") # 結果為物件list

# 對每個找到的物件再找<div class="title"><a href="...">裡的文字
for each in all_article:
    print(each.select_one("div[class=title] > a").text) # 結果為單個物件