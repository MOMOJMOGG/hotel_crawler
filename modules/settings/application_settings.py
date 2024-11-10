
from dotenv import load_dotenv
import os

# 讀取 .env 檔案
load_dotenv()


class ApplicationSettings:
    
    def __init__(self):
        self.gmap_url = "https://www.google.com.tw/maps/"
        
        self.openai_key = os.environ.get("OPAI_API_KEY")
        
        self.notion_key = os.environ.get("NOTION_API_KEY")
        self.notion_workbase = os.environ.get("NOTION_WORKPAGE_ID")
        