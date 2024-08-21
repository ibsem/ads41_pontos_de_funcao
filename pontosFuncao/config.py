import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'uma_chave_secreta_aqui'
    MONGO_URI = os.environ.get('MONGO_URI') or 'mongodb://localhost:27017/point_function_db'
