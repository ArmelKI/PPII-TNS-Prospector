from flask import Blueprint, request, jsonify, render_template
from app.models import db, Jalon, Projet, StatutJalon
from flask_login import login_required

jalons_bp = Blueprint("jalons", __name__, url_prefix="/jalons")

@jalons_bp.route("/kanban/<int:id_projet>")
@login_required
def voir_kanban(id_projet):
    """
    Display the Kanban board for a specific project.

    Args:
        id_projet (int): The ID of the project to display.

    Returns:
        Rendered HTML template for the project's Kanban board.
    """
    projet = Projet.query.get_or_404(id_projet)
    jalons = Jalon.query.filter_by(id_projet=id_projet).order_by(Jalon.date_fin_jalon).all()

    return render_template("projet_kanban.html", projet=projet, jalons=jalons)

@jalons_bp.route("/api/update_statut", methods=["POST"])
@login_required
def update_statut():
    """
    Update the status of a milestone (jalon) via an API call.

    Expects JSON data with:
        - id_jalon (int): The ID of the milestone to update.
        - nouveau_statut (str): The new status value as a string.

    Returns:
        JSON response indicating success or failure.
    """
    data = request.get_json()
    id_jalon = data.get("id_jalon")
    nouveau_statut_str = data.get("nouveau_statut")

    jalon = Jalon.query.get_or_404(id_jalon)
    for s in StatutJalon:
        if s.value == nouveau_statut_str:
            jalon.statut_jalon = s
            db.session.commit()
            return jsonify({"success": True})

    return jsonify({"success": False, "error": "Unknown status"}), 400
