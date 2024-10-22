from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import sys
import time

url = rf"https://www.agoda.com/zh-tw/?site_id=1922895&tag=e9ea26c2-c046-468f-939d-97d11075d6e0&gad_source=1&device=c&network=g&adid=695886459776&rand=11763045753665286743&expid=&adpos=&aud=kwd-2230651387&gclid=Cj0KCQjwjNS3BhChARIsAOxBM6rLcaCNeylu9YzYpHSv36KeDA1r2p4WljIZ_8umqt3VjSWqVVAId3caAqqYEALw_wcB&pslc=1&ds=tSI%2FsXiqC4YK5H39"

driver_path = 'chromedriver.exe'
service = Service(driver_path)

driver = webdriver.Chrome(service=service)

driver.get(url)

# === Place Picker ===
try:
    place_input = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-selenium='textInput']"))
    )
    place_input.send_keys('宜蘭')
    
    # -> show popup content
    pop_menu = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-selenium='autocompletePanel']"))
    )
    items = pop_menu.find_elements(By.CSS_SELECTOR, "[data-selenium='autosuggest-item']")
    print('items: ', len(items))
    
    items[0].click()
    time.sleep(3)

except Exception as e:
    print(f'Get place input error: {repr(e)}')
    sys.exit()

# === Date Picker ===
def find_date_and_click(chosed_date):
    date_picker = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, 'DatePicker__Accessible'))
    )
    
    date_elements = date_picker.find_elements(By.CSS_SELECTOR, 'span[data-selenium-date]')
    
    for element in date_elements:
        element_date = element.get_attribute('data-selenium-date')
        if element_date == chosed_date:
            trig_element = element.find_element(By.XPATH, './ancestor::*[2]')
            trig_element.click()
            print('is selected')
            break
    
try:
    check_in  = '2024-10-15'
    check_out = '2024-10-20'
    is_done = False
    
    find_date_and_click(check_in)
    
    time.sleep(1)
    
    find_date_and_click(check_out)
    
    time.sleep(2)
        
except Exception as e:
    print(f'Select datetime picker error: {repr(e)}')
    sys.exit()
    
# === Occupancy Picker ===
try:
    adult = 3
    child = 0
    room  = 2
    
    occupancy_pannel = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-selenium='occupancy-selector-panel']"))
    )
    
    occupancy_room = occupancy_pannel.find_element(By.CSS_SELECTOR, "[data-selenium='occupancyRooms']")
    cur_room = int(occupancy_room.find_element(By.XPATH, "//*[@data-selenium='desktop-occ-room-value']/p").text)
    
    room_plus = occupancy_room.find_element(By.CSS_SELECTOR, "[data-selenium='plus']")
    room_minus = occupancy_room.find_element(By.CSS_SELECTOR, "[data-selenium='minus']")
    
    while cur_room != room:
        if room > cur_room:
            room_plus.click()
        
        elif room < cur_room:
            room_minus.click()
            
        cur_room = int(occupancy_room.find_element(By.XPATH, "//*[@data-selenium='desktop-occ-room-value']/p").text)
    
    time.sleep(1)
    
    occupancy_adult = occupancy_pannel.find_element(By.CSS_SELECTOR, "[data-selenium='occupancyAdults']")
    cur_adult = int(occupancy_adult.find_element(By.XPATH, "//*[@data-selenium='desktop-occ-adult-value']/p").text)
    
    adult_plus = occupancy_adult.find_element(By.CSS_SELECTOR, "[data-selenium='plus']")
    adult_minus = occupancy_adult.find_element(By.CSS_SELECTOR, "[data-selenium='minus']")
    
    while cur_adult != adult:
        if adult > cur_adult:
            adult_plus.click()
        
        elif adult < cur_adult:
            adult_minus.click()
            
        cur_adult = int(occupancy_adult.find_element(By.XPATH, "//*[@data-selenium='desktop-occ-adult-value']/p").text)
    
    time.sleep(1)
    
    occupancy_children = occupancy_pannel.find_element(By.CSS_SELECTOR, "[data-selenium='occupancyChildren']")
    cur_children = int(occupancy_children.find_element(By.XPATH, "//*[@data-selenium='desktop-occ-children-value']/p").text)
    
    children_plus = occupancy_children.find_element(By.CSS_SELECTOR, "[data-selenium='plus']")
    children_minus = occupancy_children.find_element(By.CSS_SELECTOR, "[data-selenium='minus']")
    
    while cur_children != child:
        if child > cur_children:
            children_plus.click()
        
        elif child < cur_children:
            children_minus.click()
            
        cur_children = int(occupancy_children.find_element(By.XPATH, "//*[@data-selenium='desktop-occ-children-value']/p").text)
    
    time.sleep(1)
    
    occupancy_btn = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, 'occupancy-box'))
    )
    occupancy_btn.click()

    print('all set')

except Exception as e:
    print(f'Select occupancy picker error: {repr(e)}')
    sys.exit()

# === Search ===
try:
    search_btn = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-selenium='searchButton']"))
    )
    print('ready to search')
    time.sleep(1)
    search_btn.click()
    
except Exception as e:
    print(f'Search error: {repr(e)}')
    sys.exit()
    
time.sleep(5)

# === change to window 2 ===
try:
    window_handles = driver.window_handles
    window_handle = window_handles[1] if len(window_handles) == 2 else window_handles[0]
    
    driver.switch_to.window(window_handle)
    print(driver.title)
    
    print('switch -- success')

except Exception as e:
    print(f'Switch window error: {repr(e)}')
    sys.exit()
    
time.sleep(5)
    