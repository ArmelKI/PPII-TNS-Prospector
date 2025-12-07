"""
app.__init__ — Factory pour l'application TNS (version test-friendly)

- Accepts optional `test_config` dict that will override app.config before DB init.
- Uses `AUTO_CREATE_DB` config key to control whether to call db.create_all().
  Tests should pass {"AUTO_CREATE_DB": False, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"}
  so that create_all() is not executed on the wrong DB.
"""

# TODO supprimer les imports en trop
import os
from flask import Flask, render_template, jsonify, request
from app.models import db, Intervenant # Import des modèles
from dotenv import load_dotenv
from urllib.parse import quote
from sqlalchemy.exc import ProgrammingError
from app.models import *
from datetime import datetime
from flask_login import LoginManager

# Blueprints imports
from app.routes.dashboard import dashboard_bp
from app.routes.intervenants import intervenants_bp
from app.routes.clients import clients_bp
from app.routes.projets import projets_bp
from app.routes.interactions import interactions_bp
from app.routes.api import api_bp



load_dotenv()
login_manager = LoginManager()


def create_app():

    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = quote(os.getenv("DB_PASSWORD"))
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")
    DATABASE_URI = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

    # Initialisation de la BDD
    db.init_app(app)  # Lie la BDD à l'app

    # Initialisation du login manager
    login_manager.init_app(app)

    # Gestion d'erreur 404
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404


    # app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB

    # Enregistrement des Blueprints

    def inject_current_year():
        return {"current_year": datetime.now().year}

    app.context_processor(inject_current_year)

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(intervenants_bp)
    app.register_blueprint(clients_bp)
    app.register_blueprint(projets_bp)
    app.register_blueprint(interactions_bp)
    app.register_blueprint(api_bp)

    return app
