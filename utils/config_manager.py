import yaml
import os

class ConfigManager:
    """配置管理器，用于加载和管理应用程序配置"""
    
    def __init__(self, config_file="config.yaml"):
        """初始化配置管理器"""
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            # 如果配置文件不存在，返回默认配置
            return self.get_default_config()
    
    def get_default_config(self):
        """获取默认配置"""
        return {
            "neo4j": {
                "uri": "neo4j://localhost:7687",
                "user": "neo4j",
                "password": "password"
            },
            "llm": {
                "model": "glm-4",
                "temperature": 0.1,
                "max_tokens": 2048
            },
            "processing": {
                "chunk_size": 2000,
                "overlap": 100,
                "batch_size": 1
            }
        }
    
    def get(self, key, default=None):
        """获取配置值"""
        keys = key.split(".")
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key, value):
        """设置配置值"""
        keys = key.split(".")
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save(self):
        """保存配置到文件"""
        with open(self.config_file, "w", encoding="utf-8") as f:
            yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)

# 创建全局配置管理器实例
config_manager = ConfigManager()