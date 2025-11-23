

from flask import Blueprint, render_template

clients = Blueprint("clients", __name__)

@clients.route("/clients")
def liste_clients():
    # affichage temporaire pour éviter les erreurs
    return render_template("clients.html", clients=[])
