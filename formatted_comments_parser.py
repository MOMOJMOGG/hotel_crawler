import json
import pandas as pd
from collections import Counter

# 讀取 JSON 檔案
with open('./output/formatted-reviews.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(type(data), len(data))

positive_keys = []
negative_keys = []
summary_keys = []

for data_row in data:
    json_data = json.loads(data_row)
    
    analyze_data = json_data.get('評論分析')
    positive_list = analyze_data.get('正向評論')
    positive_keys.extend([item.get('關鍵字') for item in positive_list])
    
    negative_list = analyze_data.get('負向評論')
    negative_keys.extend([item.get('關鍵字') for item in negative_list])
    
    summary_data = json_data.get('評論總結')
    summary_keys.append(summary_data.get('評價'))

print('POS', list(positive_keys))
print('NEG', list(negative_keys))

positive_counts = Counter(positive_keys)
negative_counts = Counter(negative_keys)
summary_counts = Counter(summary_keys)

# 找出重複的正負向關鍵字
common_keywords = set(positive_counts.keys()).intersection(set(negative_counts.keys()))

print('正')
for p_key, p_cnt in positive_counts.items():
    print(p_key, p_cnt)

print('負')
for n_key, n_cnt in negative_counts.items():
    print(n_key, n_cnt)

print('common keys: ', list(common_keywords))

print('總')
for s_key, s_cnt in summary_counts.items():
    print(s_key, s_cnt)