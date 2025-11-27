import os
from flask import Flask, render_template
from dotenv import load_dotenv
from urllib.parse import quote

from app.models import *
from app.routes.intervenants import intervenants_bp
from app.models import Intervenant, Client, Projet

load_dotenv()

def create_app():
    # Chargement config DB depuis l'env
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = quote(os.getenv("DB_PASSWORD"))
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")

    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    )
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key')
    db.init_app(app)

    @app.route("/")
    def dashboard():
        nb_intervenants = Intervenant.query.count()
        nb_clients = Client.query.count()
        nb_projets = Projet.query.count()

        return render_template(
            "dashboard.html",
            nb_clients=nb_clients,
            nb_projets=nb_projets,
            nb_intervenants=nb_intervenants
        )
    
    

    # Enregistrement des blueprints
    app.register_blueprint(intervenants_bp)

    # Gestion erreur 404
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    return app
