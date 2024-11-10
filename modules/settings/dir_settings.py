import os

class DirSettings:
    
    def __init__(self, root_dir):
        self.dir_root = root_dir
        
        self.dir_engine = os.path.join(root_dir, 'engine')
        self.crawler_engine = os.path.join(self.dir_engine, 'chromedriver.exe')
        