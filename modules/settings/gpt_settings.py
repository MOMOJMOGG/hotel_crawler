from copy import deepcopy

class GPTSettings:
    
    def __init__(self):
        
        self.model = "gpt-4o-mini"
        self.prompt = [
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
            )}
        ]
        
        self.response_spec = {
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
    
    def build_message(self, review):
        message = deepcopy(self.prompt)
        message[1]['content'] += f"評論內容：\n{review}"
        return message