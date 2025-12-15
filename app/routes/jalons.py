from flask import Blueprint, request, jsonify, render_template
from app.models import db, Jalon, Projet, StatutJalon

jalons_bp = Blueprint("jalons", __name__, url_prefix="/jalons")

@jalons_bp.route("/kanban/<int:id_projet>")
def voir_kanban(id_projet):
    """
    Display the Kanban board for a specific project.

    Args:
        id_projet (int): The ID of the project to display.

    Returns:
        Rendered HTML template for the project's Kanban board.
    """
    # Fetch the project by its ID, or return 404 if not found
    projet = Projet.query.get_or_404(id_projet)
    # Get all milestones (jalons) for this project, ordered by their end date
    jalons = Jalon.query.filter_by(id_projet=id_projet).order_by(Jalon.date_fin_jalon).all()
    
    return render_template("projet_kanban.html", projet=projet, jalons=jalons)

@jalons_bp.route("/api/update_statut", methods=["POST"])
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

    # Try to fetch the milestone by its ID, or return 404 if not found
    jalon = Jalon.query.get_or_404(id_jalon)

    # Loop through all possible statuses to find a match
    for s in StatutJalon:
        if s.value == nouveau_statut_str:
            # Update the milestone's status and save to the database
            jalon.statut_jalon = s
            db.session.commit()
            return jsonify({"success": True})
            
    # If the provided status is not valid, return an error
    return jsonify({"success": False, "error": "Unknown status"}), 400