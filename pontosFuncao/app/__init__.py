from flask import Flask
from flask_pymongo import PyMongo
from config import Config

# Cria uma instância de PyMongo. Isso será usado para interagir com o banco de dados MongoDB.
mongo = PyMongo()

def create_app():
    """
    Função de fábrica do aplicativo Flask.
    Esta função configura e retorna uma instância do aplicativo Flask.
    """
    # Cria uma instância do Flask.
    app = Flask(__name__)
    
    # Carrega as configurações a partir de um objeto de configuração.
    app.config.from_object(Config)

    # Inicializa o objeto PyMongo com o aplicativo Flask configurado.
    mongo.init_app(app)

    # Importa e registra o blueprint 'main' das rotas do aplicativo.
    # Isso organiza o código de roteamento em um módulo separado, mantendo este arquivo limpo.
    from .routes import main
    app.register_blueprint(main)

    # Retornar a instância do aplicativo configurado.
    return app

