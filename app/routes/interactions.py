from flask import Blueprint, render_template

interactions = Blueprint("interactions", __name__)

@interactions.route("/interactions")
def liste_interactions():
    return render_template("interactions.html", interactions=[])
    # affichage temporaire pour éviter les erreurs
