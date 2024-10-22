
import pandas as pd

# 定義清理函數，將換行符號替換為空格並去除多餘的空格
def clean_text(comment):
    # 去除換行符號並將其替換為空格
    cleaned_comment = comment.replace('\n', ' ').strip()
    # 將多餘的多個空格替換成單一空格
    cleaned_comment = ' '.join(cleaned_comment.split())
    return cleaned_comment

# 讀取上傳的CSV檔案
file_path = 'reviews.csv'
df = pd.read_csv(file_path)

# 使用清理函數對 CSV 裡面的 'comment' 欄位進行清理
df['optimized_cleaned_comment'] = df['comment'].apply(clean_text)

# 檢查清理後的數據
df[['comment', 'optimized_cleaned_comment']].head()

# 將清理過的內容直接修改到 comment 欄位中
df['comment'] = df['optimized_cleaned_comment']

# 刪除不再需要的輔助欄位
df.drop(columns=['optimized_cleaned_comment'], inplace=True)


df.to_csv('reviews-clean.csv', index=False)