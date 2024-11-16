import json
import os

class DirSettings:
    
    def __init__(self, root_dir):
        self.dir_root = root_dir
        
        self.dir_engine = os.path.join(root_dir, 'engine')
        self.crawler_engine = os.path.join(self.dir_engine, 'chromedriver.exe')
        
        self.dir_seeds = os.path.join(root_dir, 'seeds')
        self.dir_db = os.path.join(self.dir_seeds, 'db')
        
        self.db_path = os.path.join(self.dir_db, 'hotel_reviews.db')
    
    def save_formed_file(self, filename, data):
        filepath = os.path.join(self.dir_db, f"{filename}.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        return filepath

    def read_formed_file(self, file):
        if os.path.exists(file):
            with open(file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {}