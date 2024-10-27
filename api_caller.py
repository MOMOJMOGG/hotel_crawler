
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
file_path = './output/reviews-clean.csv'
# file_path = './output/single-review.csv'
df = pd.read_csv(file_path)
# response_json_path = './output/single-review.json'
raw_response_json_path = './output/raw-formatted-reviews.json'
response_json_path = './output/formatted-reviews.json'

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

def analyze_review_with_output_spec(review):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional sentiment analysis model."},
                {"role": "user", "content": (
                    "請分析這條飯店評論，並根據輸出 JSON 格式返回結果\n"
                    "評論: 包含原始評論的完整內容\n"
                    "關鍵字: 正面或負面要素的評價關鍵字, 是考量飯店的關鍵屬性\n"
                    "評價說明: 與關鍵字有關係的評價摘要\n"
                    "評價: 總結為「推薦」或「普通」或「不推薦」的結論\n"
                    "推薦結論: 針對評論的總結分析結果\n"
                    "正面要素關鍵字可以包括：服務、衛生、設施、早餐、舒適度等。\n"
                    "負面要素關鍵字可以包括：服務、衛生、設施、隔音、位置等。\n"
                    f"評論內容：\n{review}"
                )}
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "analyze_results",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "評論": {
                                "type": "string"
                            },
                            "評論分析": {
                                "type": "object",
                                "properties": {
                                    "正向評論": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "關鍵字": {
                                                    "type": "string"
                                                },
                                                "評價說明": {
                                                    "type": "string"
                                                }
                                            },
                                            "required": ["關鍵字", "評價說明"],
                                            "additionalProperties": False
                                        }
                                    },
                                    "負向評論": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "關鍵字": {
                                                    "type": "string"
                                                },
                                                "評價說明": {
                                                    "type": "string"
                                                }
                                            },
                                            "required": ["關鍵字", "評價說明"],
                                            "additionalProperties": False
                                        }
                                    }
                                },
                                "required": ["正向評論", "負向評論"],
                                "additionalProperties": False
                            },
                            "評論總結": {
                                "type": "object",
                                "properties": {
                                    "評價": {
                                        "type": "string"
                                    },
                                    "推薦結論": {
                                        "type": "string"
                                    }
                                },
                                "required": ["評價", "推薦結論"],
                                "additionalProperties": False
                            }
                        },
                        "required": ["評論", "評論分析", "評論總結"],
                        "additionalProperties": False
                    }
                }
            }
        )
        # 返回 API 生成的分析結果
        print("Response: ", response, isinstance(response, BaseModel))
        
        return response.model_dump()
    except Exception as e:
        return f"Error: {str(e)}"

# 對所有評論進行 API 呼叫並收集回應
start = time.time()
# responses = df['comment'].apply(analyze_review_aspects)
responses = df['comment'].apply(analyze_review_with_output_spec)
print("Run: {} s".format((time.time() - start)))
print("Get: {}, type: {}".format(responses, type(responses)))

# 將原始回應結果轉換為列表
raw_responses_list = responses.tolist()
try:
    with open(raw_response_json_path, 'w', encoding='utf-8') as f:
        json.dump(raw_responses_list, f, ensure_ascii=False, indent=4)
    print(f"API 原始回應已成功保存到 {raw_response_json_path}")
    
except Exception as e:
    # 儲存失敗時備份到純文本檔案
    backup_path = './output/backup_raw_review_aspects_responses.txt'
    with open(backup_path, 'w', encoding='utf-8') as f:
        for response in raw_responses_list:
            f.write(f"{str(response)}\n")
    print(f"主儲存失敗，備份已保存到 {backup_path}. 錯誤訊息: {str(e)}")


responses_list = [data['choices'][0]['message']['content'] for data in raw_responses_list]

# 將標準化回應結果轉換為列表
try:
    with open(response_json_path, 'w', encoding='utf-8') as f:
        json.dump(responses_list, f, ensure_ascii=False, indent=4)
    print(f"API 回應已成功保存到 {response_json_path}")
    
except Exception as e:
    # 儲存失敗時備份到純文本檔案
    backup_path = './output/backup_review_aspects_responses.txt'
    with open(backup_path, 'w', encoding='utf-8') as f:
        for response in responses_list:
            f.write(f"{str(response)}\n")
    print(f"主儲存失敗，備份已保存到 {backup_path}. 錯誤訊息: {str(e)}")