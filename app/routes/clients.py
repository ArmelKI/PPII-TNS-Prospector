from flask import Blueprint, render_template
from app.models import Client 

clients_bp = Blueprint("clients", __name__, url_prefix="/clients")

@clients_bp.route("/")
def liste_clients():
    # affichage temporaire pour éviter les erreurs
    clients = Client.query.all()
    return render_template("clients.html", clients=clients)
