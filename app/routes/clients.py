from flask import Blueprint, render_template
from flask_login import login_required



clients_bp = Blueprint("clients", __name__, url_prefix="/clients")

@clients_bp.route("/")
@login_required
def liste_clients():
    # affichage temporaire pour éviter les erreurs
    return render_template("clients.html", clients=[])
