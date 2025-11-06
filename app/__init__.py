import os
from flask import Flask, render_template
from app.routes.intervenants import intervenants_bp 
from app.models import db, Intervenant # Import des modèles
from dotenv import load_dotenv
from urllib.parse import quote


load_dotenv()


def create_app():

    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = quote(os.getenv("DB_PASSWORD"))
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")
    print(DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)


    app = Flask(__name__, template_folder="templates", static_folder="static")

    # Configuration de la base de données
    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}?sslmode=require'
    
    # === AJOUT DE LA SECRET_KEY ===
    # Nécessaire pour que les 'flash messages' (sessions) fonctionnent.
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'ma-super-cle-secrete-de-dev')

    # Initialisation de la BDD
    db.init_app(app)  # Lie la BDD à l'app
   
    # === CRÉATION DES TABLES ===
    # Crée les tables (ex: 'intervenant') si elles n'existent pas déjà.
    with app.app_context():
        db.create_all()

    # === ROUTE DU TABLEAU DE BORD ===
    @app.route("/")
    def dashboard():
        nb_intervenants = Intervenant.query.count()
        nb_clients = 0  # temporaire
        nb_projets = 0  # temporaire
        return render_template(
            "dashboard.html",
            nb_clients=nb_clients,
            nb_projets=nb_projets,
            nb_intervenants=nb_intervenants)
    
    # Enregistrement des Blueprints
    app.register_blueprint(intervenants_bp)

    # Gestion d'erreur 404
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    return app