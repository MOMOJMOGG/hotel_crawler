from collections import Counter
import json
from openai import OpenAI
from pydantic import BaseModel
from modules.settings.config_manager import config


class ReviewAnalyzer:
    
    def __init__(self):
        self.client = OpenAI(
            api_key=config.app.openai_key
        )
    
    def analyze_review_with_output_spec(self, review):
        message = config.gpt.build_message(review)
        
        response = self.client.chat.completions.create(
            model=config.gpt.model,
            messages=message,
            response_format=config.gpt.response_spec
        )
        
        if isinstance(response, BaseModel):
            return response.model_dump()
    
        else:
            return {}
    
    # 取得 統計資料: 正面關鍵字 / 負面關鍵字 / 共同關鍵字 / 總評價
    def parse_key_words(self, data):
        positive_keys = []
        negative_keys = []
        summary_keys  = []
        
        for data_row in data:
            json_data = json.loads(data_row)
            
            analyze_data = json_data.get('評論分析')
            positive_list = analyze_data.get('正向評論')
            positive_keys.extend([item.get('關鍵字') for item in positive_list])
            
            negative_list = analyze_data.get('負向評論')
            negative_keys.extend([item.get('關鍵字') for item in negative_list])
            
            summary_data = json_data.get('評論總結')
            summary_keys.append(summary_data.get('評價'))

        positive_counts = Counter(positive_keys)
        negative_counts = Counter(negative_keys)
        summary_counts  = Counter(summary_keys)
            
        # 找出重複的正負向關鍵字
        common_keywords = set(positive_counts.keys()).intersection(set(negative_counts.keys()))

        return {
            'positive': positive_counts,
            'negative': negative_counts,
            'common': common_keywords,
            'summary': summary_counts
        }
    
    def filter_freq(self, data, minimum):
        result = {}
        for key, cnt in data.items():
            if cnt > minimum:
                result[key] = cnt
        
        return result

    def build_multi_select_option(self, options):
        color = ["red",  "orange", "green",
                "blue", "violet", "gray"]      
          
        result = []
        for idx, option in enumerate(options):
            result.append({
                'name': option,
                'color': color[idx % 6]
            })
        
        return result
    
    # 解析資料成頁面的需求規格
    def parse_data_to_db_spec(self, data, filterd_key):
        positive_keys = filterd_key.get('positive')
        negative_keys = filterd_key.get('negative')
        
        spec_data = []
        
        for idx, data_row in enumerate(data):
            json_data = json.loads(data_row)

            info = {}
            info['ID'] = f'{idx + 1}'
            info['review'] = json_data.get('評論')
            
            analyze_data = json_data.get('評論分析')
            positive_list = analyze_data.get('正向評論')
            negative_list = analyze_data.get('負向評論')
            
            info['positive'] = []
            for item in positive_list:
                if item.get('關鍵字') in positive_keys:
                    info['positive'].append(item.get('關鍵字'))
                    
            info['negative'] = []
            for item in negative_list:
                if item.get('關鍵字') in negative_keys:
                    info['negative'].append(item.get('關鍵字'))
                    
            summary_data = json_data.get('評論總結')
            info['star'] = summary_data.get('評價')
            info['recommand'] = summary_data.get('推薦結論')

            spec_data.append(info)
            
        return spec_data

    def build_table(self, data_list):
        star_map = {
            '推薦': '推薦 ⭐⭐⭐',
            '普通': '普通 ⭐⭐',
            '不推薦': '不推 ⭐'
        }
        
        result = []
        
        for data in data_list:
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
            star = star_map[data.get('star')]

            result.append({
                'ID': data.get('ID'),
                '推薦度': star,
                '推薦結論': data.get('recommand'),
                '正面評價數': positive_num,
                '評價比例': ratio,
                '負面評價數': negative_num,
                '正面關鍵字': ",".join(positive_list),
                '負面關鍵字': ",".join(negative_list),
                '評論': data.get('review')
            })
            
        return result
    
analyzer = ReviewAnalyzer()