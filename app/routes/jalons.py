from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from app.models import db, Jalon, Projet, StatutJalon
from datetime import date
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
    # Fetch milestones ordered by end date for better visibility
    jalons = Jalon.query.filter_by(id_projet=id_projet).order_by(Jalon.date_fin_jalon).all()

    return render_template("projet_kanban.html", projet=projet, jalons=jalons)

@jalons_bp.route("/add/<int:id_projet>", methods=["POST"])
@login_required
def ajouter_jalon(id_projet):
    """
    Adds a new milestone to an existing project.
    Redirects back to the Kanban board.
    """
    nom = request.form.get("nom_jalon")
    date_fin = request.form.get("date_fin_jalon")
    
    if not nom:
        flash("Milestone name is required.", "warning")
        return redirect(url_for('jalons.voir_kanban', id_projet=id_projet))

    # Create the new milestone
    # We default the status to 'A_VENIR' (To Do)
    j = Jalon(
        id_projet=id_projet,
        nom_jalon=nom,
        statut_jalon=StatutJalon.A_VENIR,
        date_fin_jalon=date_fin if date_fin else date.today()
    )
    db.session.add(j)
    db.session.commit()
    
    flash("Milestone added.", "success")
    return redirect(url_for('jalons.voir_kanban', id_projet=id_projet))

@jalons_bp.route("/delete/<int:id_jalon>", methods=["POST"])
@login_required
def supprimer_jalon(id_jalon):
    """
    Deletes a milestone from the database.
    """
    jalon = Jalon.query.get_or_404(id_jalon)
    id_projet = jalon.id_projet
    
    db.session.delete(jalon)
    db.session.commit()
    
    flash("Milestone deleted.", "success")
    return redirect(url_for('jalons.voir_kanban', id_projet=id_projet))

@jalons_bp.route("/api/update_statut", methods=["POST"])
@login_required
def update_statut():
    """
    Update the status of a milestone via an AJAX API call (Drag & Drop).

    Expects JSON data with:
        - id_jalon (int): The ID of the milestone to update.
        - nouveau_statut (str): The new status value as a string.
    """
    data = request.get_json()
    id_jalon = data.get("id_jalon")
    nouveau_statut_str = data.get("nouveau_statut")

    jalon = Jalon.query.get_or_404(id_jalon)
    
    # Iterate through Enum to find the matching status
    found = False
    for s in StatutJalon:
        if s.value == nouveau_statut_str:
            jalon.statut_jalon = s
            found = True
            break
            
    if found:
        db.session.commit()
        return jsonify({"success": True})

    return jsonify({"success": False, "error": "Unknown status"}), 400