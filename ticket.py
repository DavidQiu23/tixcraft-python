from selenium import webdriver
import selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.keys import Keys
import numpy as np
import cv2
import pytesseract
import requests
import time

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument("--disable-blink-features=AutomationControlled")  # 隱藏自動化痕跡
options.add_argument("--disable-gpu")  # 禁用 GPU (對 Windows 有幫助)
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-extensions')
# options.add_argument("user-data-dir=C:/Users/david/AppData/Local/Microsoft/Edge/User Data")
# options.add_argument("--profile-directory=Profile 4")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0")
# options.binary_location = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

account = input("帳號:")
pwd = input("密碼:")
game=input("表演網址:") # 25_casty

start_time = time.time()

# service = Service(executable_path=r'E:\project\suzukiami607\msedgedriver.exe')

driver = webdriver.Edge(options=options)
 # 前往 Google 登入頁面
driver.get("https://accounts.google.com/signin")

# 等待電子郵件輸入框出現
wait = WebDriverWait(driver, 30)  # 設定最大等待時間 30 秒
email_input = wait.until(EC.presence_of_element_located((By.ID, "identifierId")))

# 輸入電子郵件
email_input.send_keys(account)
email_input.send_keys(Keys.RETURN)

# 等待密碼輸入框出現
password_input = wait.until(EC.element_to_be_clickable((By.NAME, "Passwd")))

# 輸入密碼
password_input.send_keys(pwd)
password_input.send_keys(Keys.RETURN)

# 等待登入完成 (例如，檢查是否跳轉到 Google帳戶)
wait.until(EC.url_contains("myaccount.google.com"))
print("登入成功")


driver.get(f'https://tixcraft.com/activity/game/{game}')

driver.execute_script("arguments[0].click();", driver.find_element(By.ID,"loginGoogle"))

# 要測試同時多開能不能成功 同時搶多天
# 要使用不同設定檔，一個設定檔一次只能一個執行緒存取

for tr in driver.find_elements(By.CSS_SELECTOR,'table tr'):
    for td in tr.find_elements(By.CSS_SELECTOR,'td'):
        print(td.text,end="")
    print("")

date = input("第幾場:(從1開始):")
group = int(input("第幾群:(從0開始):"))

while(True):
    try:
        driver.execute_script("arguments[0].click();", driver.find_element(By.CSS_SELECTOR,f'table button:nth-child({date})'))
        break
    except selenium.common.exceptions.NoSuchElementException as e:
        print(e)
        driver.refresh()


while(True):
    try:
        driver.execute_script("arguments[0].click();", driver.find_elements(By.CSS_SELECTOR,'.zone .area-list')[group].find_element(By.CSS_SELECTOR,'li a'))
        break
    except selenium.common.exceptions.NoSuchElementException as e:
        print(e)
        if(len(driver.find_elements(By.CSS_SELECTOR,'.zone .area-list'))==int(group)+1):
            group = 0
        else:
            group += group+1

while(True):
    try:
        img=driver.find_element(By.ID,"TicketForm_verifyCode-image")
        print(img.get_attribute('src'))
        # 取得 Selenium 的 headers
        headers = {
            "User-Agent": driver.execute_script("return navigator.userAgent;")
        }

        # 取得 Selenium 的 cookies 並轉換格式
        cookies = driver.get_cookies()
        cookies_dict = {cookie['name']: cookie['value'] for cookie in cookies}

        arr = np.asarray(bytearray(requests.get(img.get_attribute('src'),cookies=cookies_dict,headers=headers).content), dtype=np.uint8)
        img = cv2.imdecode(arr, -1)
        # 灰階化 → 模糊 → 二值化 → 膨脹 → 放大
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) #灰階化
        ret, output1 = cv2.threshold(img_gray, 0, 255, cv2.THRESH_BINARY_INV+ cv2.THRESH_OTSU) #二值化
        kernel = np.ones((3, 3), np.uint8)
        dilate = cv2.dilate(output1, kernel)   #膨脹
        scaled_img = cv2.resize(dilate, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC) #放大
        text = pytesseract.image_to_string(scaled_img, lang='eng',config='--oem 3 --psm 10 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFHGIJKLMNOPQRSTUVWXYZ')
        print(text.strip().lower())

        select = Select(driver.find_element(By.CSS_SELECTOR,'form select'))
        select.select_by_index(len(select.options) - 1)
        driver.execute_script("arguments[0].checked = true;",driver.find_element(By.ID,'TicketForm_agree'))
        driver.execute_script("arguments[0].value = arguments[1];", driver.find_element(By.ID,'TicketForm_verifyCode'),text.strip().lower())
        driver.execute_script("arguments[0].click();",driver.find_element(By.CSS_SELECTOR,'button[type="submit"]'))

        # 切換到alert並嘗試接收
        alert = driver.switch_to.alert
        alert.accept()  # 點擊 "接受" 或 "確定" 按鈕，視情況可用 .dismiss() 關閉
        print("Alert is present and was closed.")
    except Exception as e:
        # 如果沒有alert
        print("No alert is present.")
        break
print("end")
driver.quit()

end_time = time.time()
execution_time = end_time - start_time
print("程式執行時間：", execution_time, "秒")
