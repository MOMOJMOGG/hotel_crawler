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

from modules.settings.config_manager import config

class HotelCrawler:
    
    def __init__(self):
        print(config.dir.crawler_engine)
        service = Service(config.dir.crawler_engine)
        self.driver = webdriver.Chrome(service=service)
        
        self.method_map = {
            'xpath': By.XPATH,
            'id': By.ID,
            'tag': By.TAG_NAME,
            'class': By.CLASS_NAME,
            'css': By.CSS_SELECTOR
        }
        
        self.df = None
    
    def open_page(self):
        self.driver.get(config.app.gmap_url)
    
    def get_visible_element(self, method, search_key):
        method = self.method_map.get(method, By.XPATH)
            
        element = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((method, search_key))
        )
        return element
    
    def get_visible_elements(self, method, search_key):
        method = self.method_map.get(method, By.XPATH)
            
        element = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_all_elements_located((method, search_key))
        )
        return element

    def find(self, element, method, search_key):
        method = self.method_map.get(method, By.XPATH)
            
        target = element.find_element(method, search_key)
        return target
    
    def finds(self, element, method, search_key):
        method = self.method_map.get(method, By.XPATH)
            
        target = element.find_elements(method, search_key)
        return target

    def scroll(self):
        pane = self.get_visible_element("css", "div[jslog='26354;mutable:true;']")
        self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", pane)

    def save(self, data, filename):
        self.df = pd.DataFrame(data, columns=["review_id", "score", "duration", "comment"])
        self.df.to_csv(filename, index=False, encoding='utf-8')
    
def detail_parser(text):
    # 正規表達式模式
    address_pattern = r"\d{3}(?:[^\d\s]{1,3})(?:縣|市)(?:[^\d\s]{1,3})(?:市|區|鄉|鎮)(?:[^\d\s]{1,5})(?:路|街|道|巷|弄)\d+號?"
    url_pattern = r"(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}"
    phone_pattern = r"\d{2,4}\s?\d{3,4}\s?\d{3,4}"
    plus_code_pattern = r"[A-Z0-9]{4}\+[A-Z0-9]{2}\s[^\d\s]{1,4}(?:縣|市)(?:[^\d\s]{1,3})(?:市|區|鄉|鎮)"
    time_pattern = r"(上午|下午)\d{1,2}:\d{2}"
    
    if re.search(address_pattern, text):
        print("匹配地址：", re.search(address_pattern, text).group(), text)
        return { 'address': text }

    if re.search(url_pattern, text):
        print("匹配網址：", re.search(url_pattern, text).group(), text)
        return { 'url': text }

    if re.search(phone_pattern, text):
        print("匹配電話：", re.search(phone_pattern, text).group(), text)
        return { 'phone': text }

    if re.search(plus_code_pattern, text):
        print("匹配 Plus Code：", re.search(plus_code_pattern, text).group(), text)
        return { 'plus_code': text }

    if re.search(time_pattern, text):
        checktimes = text.split('\n')
        time_group = {}
        for idx, checktime in enumerate(checktimes):
            print("匹配時間：", re.search(checktime, text).group())
            time_group['start' if idx == 0 else 'end'] = re.search(checktime, text).group()
        
        return { 'time': time_group }

    return {}
    
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

def parse_review_information(row, crawler):
    score = crawler.find(row, "css", "span.fzvQIb").text
    score = int(score.split('/')[0])
    
    duration = crawler.find(row, "css", "span.xRkPPb").text
    duration = duration.split(' (')[0]
    duration_in_days = parse_duration(duration.split(' (')[0])
    
    is_within_one_year = duration_in_days <= 90  # 判斷是否 三個月內 (90天)
    comment  = crawler.find(row, "css", "span.wiI7pd").text
    
    return {
        "score": score,
        "duration": duration,
        "is_within_one_year": is_within_one_year,
        "comment": comment
    }

def parse_reviews(crawler, id_set, review_list):
    cnt = len(review_list)
    reviews = crawler.finds(crawler.driver, "css", "div[data-review-id]")
    end_crawling = False
    
    for review in reviews:
        review_id = review.get_attribute('data-review-id')
        
        #* maximum reviews is 100
        if cnt == 100:
            end_crawling = True
            break
        
        if review_id not in id_set:
            #* use list to prevent no such element exist
            expand_btn = crawler.finds(review, "css", "button.w8nwRe")
            if expand_btn:
                expand_btn[0].click()
                time.sleep(0.05)    #? 50 ms
            
            comment_info = parse_review_information(review, crawler)
            #* check review is in 3 month limitation
            if not comment_info.get('is_within_one_year'):
                end_crawling = True
                break
            
            comment_info['review_id'] = review_id
            id_set.add(review_id)
            review_list.append(comment_info)
            cnt += 1
    
    return (id_set, review_list, end_crawling)

def craw_hotel(hotel):
    info = {}
    
    start = time.time()
    crawler = HotelCrawler()
    crawler.open_page()
    
    #* jump to hotel menu
    place_input = crawler.get_visible_element("xpath", "//*[@id='searchboxinput']")
    place_input.send_keys(hotel)
    
    recommand_menu = crawler.get_visible_element("id", "ydp1wd-haAclf")
    items = crawler.finds(recommand_menu, "tag", "div")
    print('Search items: ', len(items))
    
    items[0].click()
    
    #* parse hotel informations
    card_menu = crawler.get_visible_element("xpath", "//*[@id='QA0Szd']/div/div/div[1]/div[2]")
    title = crawler.find(card_menu, "css", "h1.DUwDvf")
    info['name'] = title.text
    print('Hotel Name: ', title.text)

    star_menu = crawler.get_visible_element("css", "div.dmRWX")
    front_star_menu = crawler.find(star_menu, "css", "div.F7nice")
    star = crawler.find(front_star_menu, "xpath", "./span[1]/span")
    info['star'] = star.text
    print("Star: ", star.text)
    
    comments_num = crawler.find(front_star_menu, "xpath", "./span[2]/span/span")
    print("Total comments: ", comments_num.text)
    
    rank = crawler.find(star_menu, "xpath", "./span/span/span/span[2]/span/span")
    info['rank'] = rank.text
    print('Star Rank: ', rank.text)
    
    detail_rows = crawler.get_visible_elements("css", "div.RcCsl")
    informations = {}
    for row in detail_rows:
        content = crawler.find(row, "css", "div.Io6YTe.fontBodyMedium")
        row_detail = detail_parser(content.text)
        informations.update(row_detail)
    
    info['information'] = informations
    print('Information: ', informations)
    
    #* jump to review block
    btns_menu = crawler.get_visible_element("css", "div.RWPxGd")
    btns = crawler.finds(btns_menu, "tag", "button")
    btns[2].click()
    crawler.scroll()
    time.sleep(0.1)
    
    #* max scrolling 50 times
    id_set = set()
    review_list = []
    for _ in range(50):
        result = parse_reviews(crawler, id_set, review_list)
        id_set, review_list, end_crawling = result
        if end_crawling:
            break
        
        crawler.scroll()
        time.sleep(0.05)    #? 50 ms
    
    print("Final results: ", len(review_list))
    info['review'] = review_list
    print('Total Cost: {} s'.format((time.time() - start)))
    
    return info