from flask import Blueprint, render_template

projets_bp = Blueprint("projets", __name__)

@projets_bp.route("/projets")
def liste_projets():
    return render_template("projets.html", projets=[])
    # affichage temporaire pour éviter les erreurs
