import json
from collections import Counter

data_file = './output/formatted-reviews.json'

def load_data():
    global data_file
    # 讀取 JSON 檔案
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        print('共 {} 筆'.format(len(data)))
        return data

def parse_comments():
    data = load_data()
    
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

def filter_freq(data, minimum):
    result = {}
    for key, cnt in data.items():
        if cnt > minimum:
            result[key] = cnt
    
    return result

if __name__ == '__main__':
    result = parse_comments()
    positive_result = result.get('positive')
    negative_result = result.get('negative')
    common_set = result.get('common')
    summary_result = result.get('summary')
    
    print('正面關鍵字統計')
    for p_key, p_cnt in positive_result.items():
        if p_cnt > 1:
            print(p_key, p_cnt)

    print('負面關鍵字統計')
    for n_key, n_cnt in negative_result.items():
        if n_cnt > 1:
            print(n_key, n_cnt)

    print('共同關鍵字: ', list(common_set))

    print('總評價統計')
    for s_key, s_cnt in summary_result.items():
        if s_cnt > 1:
            print(s_key, s_cnt)