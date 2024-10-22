
from dotenv import load_dotenv
import json
from openai import OpenAI
import os
import pandas as pd
from pydantic import BaseModel
import time

# 讀取 .env 檔案
load_dotenv()

# 從 .env 中取得 API 金鑰
client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPAI_API_KEY"),
)

# 讀取清理過的 CSV 檔案
file_path = 'reviews-clean.csv'
# file_path = 'single-test.csv'
df = pd.read_csv(file_path)
response_json_path = 'response_comments.json'
# response_json_path = 'single-test.json'

# 定義函數來分析評論的正面和負面要素
def analyze_review_aspects(review):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional sentiment analysis model."},
                {"role": "user", "content": (
                    f"請分析這條飯店評論，找出其中的正面和負面要素。\n"
                    f"正面要素可以包括：服務、衛生、設施、早餐、舒適度等。\n"
                    f"負面要素可以包括：服務、衛生、設施、隔音、位置等。\n"
                    f"請分別列出正面和負面要素，無論它們對評論者是否有影響。\n"
                    f"評論內容：\n{review}"
                )}
            ],
            # response_format={ "type": "json_object" }
        )
        # 返回 API 生成的分析結果
        print("Response: ", response, isinstance(response, BaseModel))
        
        # return {
        #     "id": response["id"],
        #     "model": response["model"],
        #     "created": response["created"],
        #     "content": response["choices"][0]["message"]["content"],
        #     "prompt_tokens": response["usage"]["prompt_tokens"],
        #     "completion_tokens": response["usage"]["completion_tokens"],
        #     "total_tokens": response["usage"]["total_tokens"]
        # }
        return response.model_dump()
    except Exception as e:
        return f"Error: {str(e)}"

# 對所有評論進行 API 呼叫並收集回應
start = time.time()
responses = df['comment'].apply(analyze_review_aspects)
print("Run: {} s".format((time.time() - start)))
print("Get: {}, type: {}".format(responses, type(responses)))

# 將回應結果轉換為列表
responses_list = responses.tolist()

# 儲存到 JSON 檔案，並在失敗時備份成文本文件
try:
    with open(response_json_path, 'w', encoding='utf-8') as f:
        json.dump(responses_list, f, ensure_ascii=False, indent=4)
    print(f"API 回應已成功保存到 {response_json_path}")
    
except Exception as e:
    # 儲存失敗時備份到純文本檔案
    backup_path = 'backup_review_aspects_responses.txt'
    with open(backup_path, 'w', encoding='utf-8') as f:
        for response in responses_list:
            f.write(f"{str(response)}\n")
    print(f"主儲存失敗，備份已保存到 {backup_path}. 錯誤訊息: {str(e)}")