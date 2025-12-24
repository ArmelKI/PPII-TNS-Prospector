from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import InteractionClient, Client, EtatRelation, db
from datetime import date

interactions_bp = Blueprint("interactions", __name__, url_prefix="/interactions")

@interactions_bp.route("/")
def liste_interactions():
    """
    Display a list of all client interactions, sorted by most recent first.

    Returns:
        Rendered HTML template showing all interactions.
    """
    interactions = InteractionClient.query.order_by(InteractionClient.date_interaction.desc()).all()
    return render_template("interactions.html", interactions=interactions)

@interactions_bp.route("/add", methods=["POST"])
def ajouter_interaction():
    """
    Handle form submission to add a new interaction for a client.

    Expects form data:
        - id_client: The ID of the client this interaction is for.
        - detail: Details about the interaction.
        - id_etat_relation: (Optional) The relationship status ID.

    Redirects to the client's detail page after adding.
    """
    id_client = request.form.get("id_client")
    detail = request.form.get("detail")
    inter = InteractionClient(
        id_client=id_client,
        detail_interaction=detail, 
        date_interaction=date.today(),
        id_etat_relation=request.form.get("id_etat_relation") 
    )
    db.session.add(inter)
    db.session.commit()
    flash("Interaction added successfully.", "success")
    return redirect(url_for('clients.details_client', id=id_client))