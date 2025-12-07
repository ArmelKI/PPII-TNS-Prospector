from flask import Blueprint, render_template

interactions_bp = Blueprint("interactions", __name__)

@interactions_bp.route("/interactions")
def liste_interactions():
    return render_template("interactions.html", interactions=[])
    # affichage temporaire pour éviter les erreurs
