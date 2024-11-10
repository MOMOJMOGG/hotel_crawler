from modules.settings.application_settings import ApplicationSettings
from modules.settings.dir_settings import DirSettings
from modules.settings.gpt_settings import GPTSettings

#* 全域變數管理
class ConfigManager:
    
    def __init__(self):
        self.app = None
        self.dir = None
        self.gpt = None
    
    def load_settings(self, root_dir):
        self.app = ApplicationSettings()
        self.dir = DirSettings(root_dir)
        self.gpt = GPTSettings()
    
    
config = ConfigManager()