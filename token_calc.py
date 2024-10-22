import tiktoken
import pandas as pd

file = "reviews-clean.csv"

# 讀取 CSV 檔案
df = pd.read_csv(file)

# 設定 Token 編碼模型
enc = tiktoken.encoding_for_model("gpt-4-turbo")

# 定義函數來計算每條評論的 Token 數量
def count_tokens(comment):
    tokens = enc.encode(comment)
    return len(tokens)

# 計算每條評論的 Token 數量並加入到 DataFrame 中
df['token_count'] = df['comment'].apply(count_tokens)

# 檢視加上 Token 計數後的 DataFrame
print(df[['comment', 'token_count']].head())

# 計算總 Token 數量
total_tokens = df['token_count'].sum()

# 每 1000 Token 的費用（以 GPT-4 Turbo 為例）
cost_per_1000_tokens = 0.03

# 計算總費用
estimated_cost = (total_tokens / 1000) * cost_per_1000_tokens
print(f"預計 API 請求費用：${estimated_cost:.4f}")