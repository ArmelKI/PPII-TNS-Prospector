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

# Blueprints imports
from app.routes.dashboard import dashboard_bp
from app.routes.intervenants import intervenants_bp
from app.routes.clients import clients_bp
from app.routes.projets import projets_bp
from app.routes.interactions import interactions_bp
from app.routes.api import api_bp




from app.models import *
#from app.routes.intervenants import intervenants_bp
from app.models import Intervenant, Client, Projet

load_dotenv()

def create_app():
    # Chargement config DB depuis l'env
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



    client.raison_sociale = client_data.get("raison_sociale", client.raison_sociale)
    client.mail_client = client_data.get("mail_client", client.mail_client)
    client.telephone_client = client_data.get("telephone_client", client.telephone_client)
    client.secteur = client_data.get("secteur", client.secteur)
    client.date_dernier_contact = client_data.get("date_dernier_contact", client.date_dernier_contact)
    client.latitude = client_data.get("latitude", client.latitude)
    client.longitude = client_data.get("longitude", client.longitude)

    db.session.commit()
    return jsonify({"message": "Client updated", "client": client_data})

    @app.route("/clients/<int:id_client>", methods=["DELETE"])
    def delete_client(id_client):
        client = Client.query.get_or_404(id_client)
        try:
            db.session.delete(client)
            db.session.commit()
        except ProgrammingError as e:
            db.session.rollback()  # important pour ne pas bloquer la session
            return jsonify({"Erreur":"", "details": str(e)}), 500
        
        return jsonify({"message": f"Client {id_client} deleted"})




    # Enregistrement des blueprints
    #app.register_blueprint(intervenants_bp)

    # Gestion erreur 404
    """
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
    """

    return app
