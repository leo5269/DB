from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# 選擇使用Edge瀏覽器開啟
driver = webdriver.Edge()
driver.get("https://www.google.com/")

try:
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "textarea[aria-label='搜尋']")))
    input_block = driver.find_element(By.CSS_SELECTOR, "textarea[aria-label='搜尋']")
    input_block.send_keys("中央大學")
    input_block.send_keys(Keys.ENTER)

    input("Press Enter to exit...")  ## 在Terminal按下Enter會執行driver.quit()
    
    driver.quit()
except TimeoutException as e:
    print(e)  
