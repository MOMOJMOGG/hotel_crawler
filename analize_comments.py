import json
import pandas as pd

# 讀取 JSON 檔案
with open('output/response_comments.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 初始化列表來保存匯總的資料
positive_aspects = []
negative_aspects = []
total_prompt_tokens = 0
total_completion_tokens = 0
total_tokens = 0

# 解析每筆資料
for item in data:
    # 取得評論的內容
    content = item['choices'][0]['message']['content']
    
    # 分析正面和負面要素
    if '正面要素：' in content:
        positive = content.split('正面要素：')[1].split('負面要素：')[0].strip()
        positive_aspects.append(positive)
    
    if '負面要素：' in content:
        negative = content.split('負面要素：')[1].strip()
        negative_aspects.append(negative)
    
    # 取得 token 使用情況
    usage = item.get('usage', {})
    total_prompt_tokens += usage.get('prompt_tokens', 0)
    total_completion_tokens += usage.get('completion_tokens', 0)
    total_tokens += usage.get('total_tokens', 0)

# 將正面和負面要素合併為 DataFrame 以便分析
df_summary = pd.DataFrame({
    'positive_aspects': positive_aspects,
    'negative_aspects': negative_aspects
})

df_summary.to_csv('output/element.json', encoding='utf-8')
print("要素解析 JSON 文件。")

# 統計各要素的出現次數
# positive_counts = df_summary['positive_aspects'].str.split('\n').explode().value_counts()
# negative_counts = df_summary['negative_aspects'].str.split('\n').explode().value_counts()

# 顯示總的 token 用量
print(f"總提示 tokens: {total_prompt_tokens}")
print(f"總回應 tokens: {total_completion_tokens}")
print(f"總使用 tokens: {total_tokens}")

# 將結果保存為 CSV 文件
# positive_counts.to_csv('positive_aspects_summary.csv', encoding='utf-8')
# negative_counts.to_csv('negative_aspects_summary.csv', encoding='utf-8')

# print("正面和負面要素的統計已保存為 CSV 文件。")
