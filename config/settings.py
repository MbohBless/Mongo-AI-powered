import os 
from dotenv import load_dotenv
import logging
load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'my_precious')
    DEBUG = os.getenv('DEBUG', "False").lower() in ("true", "1", "t")
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/flask-mongo')
    MONGODB_DB = os.getenv('MONGODB_DB', 'flask-mongo')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_API_URL = os.getenv('OPENAI_API_URL',None)
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'WARNING')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    
class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
    
app_config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}


def get_config(env = 'development'):
    return app_config.get(env, DevelopmentConfig)