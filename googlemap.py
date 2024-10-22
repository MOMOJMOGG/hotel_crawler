from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from datetime import datetime
import pandas as pd
import sys
import time
import re

TARGET_HOTEL = '煙波大飯店宜蘭館'

url = "https://www.google.com.tw/maps/"

driver_path = 'chromedriver.exe'
service = Service(driver_path)

driver = webdriver.Chrome(service=service)

driver.get(url)

time.sleep(3)

try:
    place_input = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, "//*[@id='searchboxinput']"))
    )
    place_input.send_keys(TARGET_HOTEL)
    
    # -> show popup content
    recommand_menu = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "ydp1wd-haAclf"))
    )
    items = recommand_menu.find_elements(By.TAG_NAME, "div")
    print('Search items: ', len(items))
    
    time.sleep(1)
    
    items[0].click()
    
except Exception as e:
    print(f'Get place input error: {repr(e)}')
    sys.exit()

# === parse information
try:
    card_menu = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, "//*[@id='QA0Szd']/div/div/div[1]/div[2]"))
    )
    title = card_menu.find_element(By.CSS_SELECTOR, "h1.DUwDvf")
    print('Hotel: ', title.text)
    
    time.sleep(1)
    
except Exception as e:
    print(f'Parse place information error: {repr(e)}')
    sys.exit()

# === star information ===
try:
    star_menu = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "div.dmRWX"))
    )
    front_star_menu = star_menu.find_element(By.CSS_SELECTOR, "div.F7nice")
    star = front_star_menu.find_element(By.XPATH, './span[1]/span')
    print('Star: ', star.text)
    
    comments_num = front_star_menu.find_element(By.XPATH, './span[2]/span/span')
    print('Comments: ', comments_num.text)
    
    attr = star_menu.find_element(By.XPATH, './span/span/span/span[2]/span/span')
    print('Attributes: ', attr.text)
    
    time.sleep(0.5)
    
except Exception as e:
    print(f'Parse star information error: {repr(e)}')
    sys.exit()
    
# === Buttons ===
try:
    btns_menu = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "div.RWPxGd"))
    )
    btns = btns_menu.find_elements(By.TAG_NAME, 'button')
    print('Control Button:', len(btns))
    
    time.sleep(0.5)

except Exception as e:
    print(f'Get controll btns error: {repr(e)}')
    sys.exit()

# === Detail ===
def check_pattern(text):
    # 正規表達式模式
    address_pattern = r"\d{3}(?:[^\d\s]{1,3})(?:縣|市)(?:[^\d\s]{1,3})(?:市|區|鄉|鎮)(?:[^\d\s]{1,5})(?:路|街|道|巷|弄)\d+號?"
    url_pattern = r"(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}"
    phone_pattern = r"\d{2,4}\s?\d{3,4}\s?\d{3,4}"
    plus_code_pattern = r"[A-Z0-9]{4}\+[A-Z0-9]{2}\s[^\d\s]{1,4}(?:縣|市)(?:[^\d\s]{1,3})(?:市|區|鄉|鎮)"
    time_pattern = r"(上午|下午)\d{1,2}:\d{2}"

    # 匹配並列印結果
    if re.search(address_pattern, text):
        print("匹配地址：", re.search(address_pattern, text).group(), text)

    if re.search(url_pattern, text):
        print("匹配網址：", re.search(url_pattern, text).group(), text)

    if re.search(phone_pattern, text):
        print("匹配電話：", re.search(phone_pattern, text).group(), text)

    if re.search(plus_code_pattern, text):
        print("匹配 Plus Code：", re.search(plus_code_pattern, text).group(), text)

    if re.search(time_pattern, text):
        checktimes = text.split('\n')
        for checktime in checktimes:
            print("匹配時間：", re.search(checktime, text).group())
        
try:
    detail_rows = WebDriverWait(driver, 10).until(
        EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "div.RcCsl"))
    )
    print('Detail: ', len(detail_rows))
    
    for row in detail_rows:
        mark_row = row.find_element(By.CSS_SELECTOR, 'div.cXHGnc')
        content  = row.find_element(By.CSS_SELECTOR, 'div.Io6YTe.fontBodyMedium')
        check_pattern(content.text)
    time.sleep(0.5)

except Exception as e:
    print(f'Get detail information error: {repr(e)}')
    sys.exit()

# === Comment button ===
def exec_scroll():
    print('try scroll')
    pane = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "div[jslog='26354;mutable:true;']"))
    )
    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", pane)
    print('scroll')
    
try:
    comment_btn = btns[2]
    comment_btn.click()
    
    print('click comment btn')
    time.sleep(0.5)
    
    #* exec scroll
    exec_scroll()
    time.sleep(0.5)

except Exception as e:
    print(f'Click comment button error: {repr(e)}')
    sys.exit()

# === Get comments ===
review_ids = set()
review_data = []
stop_date_limit = datetime.now().replace(year=datetime.now().year - 2)  #? 保留 1 - 2 年的留言

cnt = 0
def get_review_rows():
    global cnt
    reviews = driver.find_elements(By.CSS_SELECTOR, "div[data-review-id]")
    print('Scan reviews: ', len(reviews))
    for review in reviews:
        review_id = review.get_attribute('data-review-id')
        if cnt == 100:
            return False
        
        if review_id not in review_ids:
            expand_btn = review.find_elements(By.CSS_SELECTOR, 'button.w8nwRe.kyuRq')
            if expand_btn:
                expand_btn[0].click()
                #* click and wait
                time.sleep(0.1)
            
            comment_info = parse_comment(review)
            if not comment_info.get('is_within_one_year'):
                return False
            
            review_ids.add(review_id)
            comment_info['review_id'] = review_id
            review_data.append(comment_info)
            
            # 處理評論邏輯，如儲存或進一步解析
            print(f"第 {cnt} 筆 | 抓取到評論 ID: {review_id}")
            cnt += 1
            
    return True  # 繼續抓取

def parse_duration(duration_text):
    # 使用正則表達式來解析時間範圍
    match = re.match(r'(\d+)\s*(週|個月|年|天|日)', duration_text)
    if match:
        number = int(match.group(1))
        unit = match.group(2)

        if unit in ['週']:
            return number * 7  # 一週7天
        elif unit in ['個月']:
            return number * 30  # 一個月假設30天
        elif unit in ['年']:
            return number * 365  # 一年365天
        elif unit in ['天', '日']:
            return number  # 直接是天數

    # 無法解析的情況下，返回一個較大的天數，視為超過一年
    return float('inf')

def parse_comment(row):
    score = row.find_element(By.CSS_SELECTOR, 'span.fzvQIb').text
    score = int(score.split('/')[0])
    
    duration = row.find_element(By.CSS_SELECTOR, 'span.xRkPPb').text
    duration_in_days = parse_duration(duration.split(' (')[0])
    # is_within_one_year = duration_in_days <= 365  # 判斷是否一年內
    is_within_one_year = duration_in_days <= 100  # 判斷是否 三個月內 (100天)
    comment  = row.find_element(By.CSS_SELECTOR, 'span.wiI7pd').text
    
    # print('Review Score:', score)
    # print('Review duration:', duration.split(' (')[0])
    # print('Comment:', comment)
    
    return {
        "score": score,
        "duration": duration.split(' (')[0],
        "is_within_one_year": is_within_one_year,
        "comment": comment
    }

def save_to_csv(data, filename="reviews.csv"):
    # 使用 pandas 將數據保存為 CSV
    df = pd.DataFrame(data, columns=["review_id", "score", "duration", "comment"])
    df.to_csv(filename, index=False, encoding='utf-8')
    print(f"評論資訊已儲存至 {filename}")
    
try:
    
    # comment_rows = WebDriverWait(driver, 10).until(
    #     EC.visibility_of_all_elements_located((By.CSS_SELECTOR, 'div.jftiEf.fontBodyMedium'))
    # )
    # print('C len:', len(comment_rows))
    for _ in range(100):
        ans = get_review_rows()
        if not ans:
            break
        
        exec_scroll()
        time.sleep(0.1)
        
    time.sleep(1)
    print('Save review data')
    
    save_to_csv(review_data)
    time.sleep(3)
    
except Exception as e:
    print(f'Scroll and Get comments error: {repr(e)}')
    sys.exit()