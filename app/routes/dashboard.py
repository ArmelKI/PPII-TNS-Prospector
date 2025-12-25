from flask import Blueprint, render_template
from app.models import Client, Projet, Intervenant, Jalon, InteractionClient, StatutJalon, StatutProjet
from datetime import date, timedelta
from sqlalchemy import or_

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/")
def dashboard():
    """
    Renders the main dashboard page with key metrics, urgent milestones,
    recent client interactions, and project statistics.

    Returns:
        Rendered HTML template for the dashboard.
    """
    # Count total clients in the system
    nb_clients = Client.query.count()

    # Count active projects (those that are 'in progress' or 'blocked')
    nb_projets = Projet.query.filter(
        Projet.statut_projet.in_([StatutProjet.EN_COURS, StatutProjet.BLOQUE])
    ).count()

    # Count total team members/intervenants
    nb_intervenants = Intervenant.query.count()

    # Find urgent milestones: those not finished and due within the next 60 days
    today = date.today()
    deadline = today + timedelta(days=60)
    jalons_urgents = Jalon.query.filter(
        Jalon.date_fin_jalon <= deadline,
        Jalon.statut_jalon != StatutJalon.PASSE  # Only milestones not marked as 'done'
    ).order_by(Jalon.date_fin_jalon.asc()).limit(6).all()

    # Get the 5 most recent client interactions (for quick follow-up)
    dernieres_interactions = InteractionClient.query.order_by(
        InteractionClient.date_interaction.desc()
    ).limit(5).all()

    # Gather all projects to compute statistics by status
    projets = Projet.query.all()
    stats = {
        "Pas commencé": 0,
        "En cours": 0,
        "Terminé": 0,
        "Bloqué": 0
    }

    for p in projets:
        # Use the string value of the Enum for status
        val = p.statut_projet.value
        if val in stats:
            stats[val] += 1
        else:
            # If status is unexpected (like 'Stand-By'), count it as 'In progress'
            stats["En cours"] += 1

    # Prepare lists for charting in the template
    labels = list(stats.keys())
    counts = list(stats.values())

    return render_template(
        "dashboard.html",
        nb_clients=nb_clients,
        nb_projets=nb_projets,
        nb_intervenants=nb_intervenants,
        jalons_urgents=jalons_urgents,
        dernieres_interactions=dernieres_interactions,
        projets_labels=labels,
        projets_counts=counts,
        stats_dict=stats  # Pass the full stats dict for raw HTML display if needed
    )
