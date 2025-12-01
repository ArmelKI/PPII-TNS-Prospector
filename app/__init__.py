"""
app.__init__ — Factory pour l'application TNS (version test-friendly)

- Accepts optional `test_config` dict that will override app.config before DB init.
- Uses `AUTO_CREATE_DB` config key to control whether to call db.create_all().
  Tests should pass {"AUTO_CREATE_DB": False, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"}
  so that create_all() is not executed on the wrong DB.
"""

import os
from flask import Flask, render_template, jsonify, request
from app.routes.intervenants import intervenants_bp
from app.models import db, Intervenant # Import des modèles
from dotenv import load_dotenv
from urllib.parse import quote
from sqlalchemy.exc import ProgrammingError
from sqlalchemy import inspect, create_engine, text
from app.models import *
from datetime import datetime


load_dotenv()


def create_app():

    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = quote(os.getenv("DB_PASSWORD"))
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")
    DATABASE_URI = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

    app = Flask(__name__, template_folder="templates", static_folder="static")

    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

    # Initialisation de la BDD
    db.init_app(app)  # Lie la BDD à l'app


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


    @app.route("/clients", methods=["GET"])
    def all_clients():
        clients = Client.query.all()
        output = []
        for client in clients:
            current_client = {}
            current_client["raison_sociale"] = client.raison_sociale
            output.append(current_client)
        return jsonify(output)

    @app.route("/clients", methods=["POST"])
    def add_client():
        client_data = request.get_json()
        client = Client(
            id_client=client_data["id_client"],
            raison_sociale=client_data["raison_sociale"],
            mail_client=client_data["mail_client"],
            telephone_client=client_data["telephone_client"],
            secteur=client_data["secteur"],
            date_dernier_contact=client_data["date_dernier_contact"],
            latitude=client_data["latitude"],
            longitude=client_data["longitude"]
        )
        db.session.add(client)
        db.session.commit()
        return jsonify(client_data)

    @app.route("/clients/<int:id_client>", methods=["PUT"])
    def update_client(id_client):
        client_data = request.get_json()
        client = Client.query.get_or_404(id_client) # si le client n'est pas trouvé -> 404

        client.raison_sociale = client_data.get("raison_sociale", client.raison_sociale)
        client.mail_client = client_data.get("mail_client", client.mail_client)
        client.telephone_client = client_data.get("telephone_client", client.telephone_client)
        client.secteur = client_data.get("secteur", client.secteur)
        client.dernier_contact = client_data.get("dernier_contact", client.dernier_contact)
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


    # Enregistrement des Blueprints
    # app.register_blueprint(intervenants_bp)

    # Gestion d'erreur 404
    # @app.errorhandler(404)
    # def page_not_found(e):
        # return render_template('404.html'), 404

    # from app.routes.media import media_bp
    # app.register_blueprint(media_bp)

    # from .routes.clients import clients
    # app.register_blueprint(clients)

    # from .routes.projets import projets
    # app.register_blueprint(projets)

    # from .routes.interactions import interactions
    # app.register_blueprint(interactions)

    # app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB

    # app.context_processor(inject_current_year)

    return app

# def inject_current_year():
#     return {"current_year": datetime.now().year}
