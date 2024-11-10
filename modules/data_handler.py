import pandas as pd
import time
from modules.review_analizer import analyzer

class DataHandler:
    
    def __init__(self, data):
        self.data = data
        self.df = pd.DataFrame(data)
        
        self.formed_data = []
    
    #* 將換行符號替換為空格並去除多餘的空格
    def clean_text(self, content):
        cleaned_content = content.replace('\n', ' ').strip()
        # 將多餘的多個空格替換成單一空格
        cleaned_content = ' '.join(cleaned_content.split())
        return cleaned_content

    def exec_clean(self, key):
        # 使用清理函數對 CSV 裡面的 KEY 欄位進行清理
        self.df['cleaned'] = self.df[key].apply(self.clean_text)
        
        # 檢查清理後的數據
        self.df[['comment', 'cleaned']].head()
        
        # 將清理過的內容直接修改到 KEY 欄位中
        self.df[key] = self.df['cleaned']
        
        # 刪除不再需要的輔助欄位
        self.df.drop(columns=['cleaned'], inplace=True)
    
    def exec_analyze(self, key):
        start = time.time()
        responses = self.df[key].apply(analyzer.analyze_review_with_output_spec)
        print("Run: {} s".format((time.time() - start)))
        
        # 將原始回應結果轉換為列表
        raw_responses_list = responses.tolist()
        self.formed_data = [data['choices'][0]['message']['content'] for data in raw_responses_list]
