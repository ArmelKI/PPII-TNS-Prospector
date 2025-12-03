from flask import Blueprint, render_template


clients_bp = Blueprint("clients", __name__, url_prefix="/clients")

@clients_bp.route("/")
def liste_clients():
    # affichage temporaire pour éviter les erreurs
    return render_template("clients.html", clients=[])
