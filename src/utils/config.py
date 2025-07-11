import os
import yaml

class Config:
    def __init__(self, config_file='config/settings.yaml'):
        self.config_file = config_file
        self.settings = self.load_config()

    def load_config(self):
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(f"Configuration file not found: {self.config_file}")
        
        with open(self.config_file, 'r') as file:
            return yaml.safe_load(file)

    def get(self, key, default=None):
        return self.settings.get(key, default)

    def set(self, key, value):
        self.settings[key] = value
        self.save_config()

    def save_config(self):
        with open(self.config_file, 'w') as file:
            yaml.dump(self.settings, file)


# Standalone function for backward compatibility
def load_config(config_file='config/settings.yaml'):
    """
    Load configuration settings from YAML file.
    Returns the configuration dictionary.
    """
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Configuration file not found: {config_file}")
    
    with open(config_file, 'r') as file:
        return yaml.safe_load(file)