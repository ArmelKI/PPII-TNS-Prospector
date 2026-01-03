from flask import Blueprint, render_template, flash
from app.models import Client, Projet, Intervenant, Jalon, InteractionClient, StatutJalon, StatutProjet
from datetime import date, timedelta
from sqlalchemy import or_
from flask_login import login_required

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/")
@login_required
def dashboard():
    """
    Renders the main dashboard page with key metrics, urgent milestones,
    recent client interactions, and project statistics.

    Returns:
        Rendered HTML template for the dashboard.
    """
    nb_clients = Client.query.count()

    nb_projets = Projet.query.filter(
        Projet.statut_projet.in_([StatutProjet.EN_COURS, StatutProjet.BLOQUE])
    ).count()

    nb_intervenants = Intervenant.query.count()

    today = date.today()
    deadline = today + timedelta(days=60)
    jalons_urgents = Jalon.query.filter(
        Jalon.date_fin_jalon <= deadline,
        Jalon.statut_jalon != StatutJalon.PASSE
    ).order_by(Jalon.date_fin_jalon.asc()).limit(6).all()

    dernieres_interactions = InteractionClient.query.order_by(
        InteractionClient.date_interaction.desc()
    ).limit(5).all()

    projets = Projet.query.all()
    stats = {
        "Pas commencé": 0,
        "En cours": 0,
        "Terminé": 0,
        "Bloqué": 0
    }

    for p in projets:
        val = p.statut_projet.value
        if val in stats:
            stats[val] += 1
        else:
            stats["En cours"] += 1

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
        stats_dict=stats
    )
