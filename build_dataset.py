
from dotenv import load_dotenv
from formatted_comments_parser import load_data
from formatted_comments_parser import filter_freq
from formatted_comments_parser import parse_comments
import json
import os
import requests
import time

TARGET_HOTEL = '煙波大飯店宜蘭館'

# 載入 Notion API 金鑰
load_dotenv()
notion_token = os.getenv("NOTION_API_KEY")
headers = {
    "Authorization": f"Bearer {notion_token}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

page_id = '12c97fdfec6d8051bbb8e08044527086'
data_file = './output/formatted-reviews.json'

# 定義 Notion 資料庫的結構
def build_db_spec(positive_list, negative_list):
    return {
        "ID": {
            "title": {}
        },
        "推薦度": {
            "select": {
                "options": [
                    {
                        "name": "推薦 ⭐⭐⭐",
                        "color": "yellow"
                    },
                    {
                        "name": "普通 ⭐⭐",
                        "color": "blue"
                    },
                    {
                        "name": "不推 ⭐",
                        "color": "red"
                    }
                ]
            }
        },
        "推薦結論": {
            "rich_text": {}
        },
        "正面評價數": {
            "number": {
                "format": "number"
            }
        },
        "評價比例": {
            "number": {
                "format": "number",
            }
        },
        "負面評價數": {
            "number": {
                "format": "number"
            }
        },
        "正面關鍵字": {
            "type": "multi_select",
            "multi_select": {
                "options": positive_list
            }
        },
        "負面關鍵字": {
            "type": "multi_select",
            "multi_select": {
                "options": negative_list
            }
        },
        "評論": {
            "rich_text": {}
        }
    }

# 創建資料庫
def create_database(page_id, database_name, properties):
    url = "https://api.notion.com/v1/databases/"
    payload = {
        "parent": {
            "type": "page_id",
            "page_id": page_id
        },
        "title": [{
            "type": "text",
            "text": {
                "content": database_name
            }
        }],
        'icon': {
            'type': 'external',
            'external': {
                'url': 'https://www.notion.so/icons/bed_gray.svg'
            }
        },
        "properties": properties
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

# 讀取資料庫
def query_database(database_id, sort_option):
    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    payload = {
        "sorts": [
            {
            "property": sort_option,
            "direction": "ascending"
            }
        ]
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

# 創建資料庫中的頁面
def create_database_page(database_id, properties):
    url = f"https://api.notion.com/v1/pages/"
    payload = {
        "parent": {
            "database_id": database_id
        },
        "properties": properties
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

# 建構多選選項的資料結構
def build_multi_select_option(options):
    color = ["red",  "orange", "yellow", "green",
             "blue", "purple", "pink", "gray", "brown"]
    
    result = []
    for idx, option in enumerate(options):
        result.append({
            'name': option,
            'color': color[idx % 9]
        })
    
    return result

# 建構頁面的資料結構
def build_db_data_page(data_dict, option_map):
    spec_date = []
    
    for key, data in data_dict.items():
        positive_list = data.get('positive')
        negative_list = data.get('negative')
        positive_num = len(positive_list)
        negative_num = len(negative_list)
        
        # 評價總數
        total_num = positive_num + negative_num
        if total_num == 0:
            continue
        
        # 評價比例
        ratio = round((positive_num / total_num) * 100, 2)
        
        # 總評價
        star = data.get('star')
        
        # 多選選項的 ID
        positive_options = [{"id": option_map['positive'][item.get('key')]['id']} for item in positive_list]
        negative_options = [{"id": option_map['negative'][item.get('key')]['id']} for item in negative_list]
        
        spec_date.append({
            "ID": {
                "title": [
                    {
                        "text": {
                            "content": key
                        }
                    }
                ]
            },
            "推薦度": {
                "select": {
                    "id": option_map['star'][star]['id']
                }
            },
            "推薦結論": {
                "rich_text": [{
                    "type": "text",
                    "text": {
                        "content": data.get('recommand'),
                        "link": None
                    },
                }]
            },
            "正面評價數": {
                "number": positive_num
            },
            "評價比例": {
                "number": ratio
            },
            "負面評價數": {
                "number": negative_num
            },
            "正面關鍵字": {
                "type": "multi_select",
                "multi_select": positive_options
            },
            "負面關鍵字": {
                "type": "multi_select",
                "multi_select": negative_options
            },
            "評論": {
                "rich_text": [{
                    "type": "text",
                    "text": {
                        "content": data.get('review'),
                        "link": None
                    },
                }]
            }
        })
    
    return spec_date

# 解析資料庫多選選項的ID
def parse_option_id_map(spec_properties):
    option_map = {
        'star': {},
        'positive': {},
        'negative': {}
    }
    star_col = spec_properties.get('推薦度')
    star_options = star_col['select']['options']
    
    # 建立 總評價-ID 對照表
    for option in star_options:
        if option['name'] == '推薦 ⭐⭐⭐':
            option_map['star']['推薦'] = {
                'id': option['id'],
                'name': option['name']
            }
    
        elif option['name'] == '普通 ⭐⭐':
            option_map['star']['普通'] = {
                'id': option['id'],
                'name': option['name']
            }
        
        else:
            option_map['star']['不推薦'] = {
                'id': option['id'],
                'name': option['name']
            }
            
    # 建立 正面關鍵字-ID 對照表
    positive_col = spec_properties.get('正面關鍵字')
    positive_options = positive_col['multi_select']['options']
    
    for option in positive_options:
        option_map['positive'][option['name']] = {
            'id': option['id'],
            'name': option['name']
        }

    # 建立 負面關鍵字-ID 對照表
    negative_col = spec_properties.get('負面關鍵字')
    negative_options = negative_col['multi_select']['options']
    
    for option in negative_options:
        option_map['negative'][option['name']] = {
            'id': option['id'],
            'name': option['name']
        }
    
    return option_map

# 解析資料成頁面的需求規格
def parse_data_to_db_spec(data, filterd_key):
    positive_keys = filterd_key.get('positive')
    negative_keys = filterd_key.get('negative')
    
    spec_data = {}
    
    for idx, data_row in enumerate(data):
        json_data = json.loads(data_row)

        info = {}
        info['review'] = json_data.get('評論')
        
        analyze_data = json_data.get('評論分析')
        positive_list = analyze_data.get('正向評論')
        negative_list = analyze_data.get('負向評論')
        
        info['positive'] = []
        for item in positive_list:
            if item.get('關鍵字') in positive_keys:
                info['positive'].append({
                    'key': item.get('關鍵字'),
                    'comment': item.get('評價說明')
                })
                
        info['negative'] = []
        for item in negative_list:
            if item.get('關鍵字') in negative_keys:
                info['negative'].append({
                    'key': item.get('關鍵字'),
                    'comment': item.get('評價說明')
                })
                
        summary_data = json_data.get('評論總結')
        info['star'] = summary_data.get('評價')
        info['recommand'] = summary_data.get('推薦結論')
        
        # 用 ID 當評論鍵值
        spec_data[f'{idx + 1}'] = info
    
    return spec_data
    
if __name__ == "__main__":
    # 取得 統計資料: 正面關鍵字 / 負面關鍵字 / 共同關鍵字 / 總評價
    calc_result = parse_comments()
    
    positive_result = calc_result.get('positive')
    negative_result = calc_result.get('negative')
    common_set = calc_result.get('common')
    summary_result = calc_result.get('summary')
    
    # 只保留關鍵字被提及超過一次的
    positive_result = filter_freq(positive_result, 1)
    negative_result = filter_freq(negative_result, 1)
    
    # 取得 關鍵字 多選選項-ID 對照表
    positive_options = build_multi_select_option(positive_result.keys())
    negative_options = build_multi_select_option(negative_result.keys())
    
    filterd_key = {
        'positive': positive_result.keys(),
        'negative': negative_result.keys()
    }
    
    # 建構 資料庫 屬性規格
    properties = build_db_spec(positive_options, negative_options)
    
    try:
        # 創建資料庫
        db_spec = create_database(page_id, TARGET_HOTEL, properties)
        print('Create database spec: ', db_spec)
        
        # 取得 資料庫 規格 與 ID
        spec_properties = db_spec.get('properties')
        database_id = db_spec.get('id')
        
        # 解析出 多選屬性欄位的 ID
        option_map = parse_option_id_map(spec_properties)
        
        # 取得評論資料
        data = load_data()
        
        # 解析評論資料 並滿足資料庫 關鍵字條件
        data_dict = parse_data_to_db_spec(data, filterd_key)
        print(f'加載資料共: {len(data_dict)} 筆')
        
        # 建構 資料庫 頁面規格
        pages = build_db_data_page(data_dict, option_map)
        print(len(pages))
        
        # 創建資料庫 頁面
        for page in pages:
            response = create_database_page(database_id, page)
            print(response)
            # 一秒建構 3 頁
            time.sleep(0.33)
            
    except Exception as e:
        print(f'Create Failed: {repr(e)}')