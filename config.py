import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DEBUG = True
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI')