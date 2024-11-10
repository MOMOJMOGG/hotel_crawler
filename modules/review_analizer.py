from modules.settings.config_manager import config
from openai import OpenAI
from pydantic import BaseModel


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

analyzer = ReviewAnalyzer()