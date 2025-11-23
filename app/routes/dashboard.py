# app/routes/dashboard.py

"""
Blueprint du tableau de bord.
Contient uniquement la logique d'affichage des statistiques
pour éviter de mélanger avec __init__.py.
"""

from flask import Blueprint, render_template
from app.models import Client, Projet, Intervenant, InteractionClient, StatutProjet
from sqlalchemy import func
from datetime import datetime, timedelta

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")

@dashboard_bp.route("/")
def dashboard():
    """
    Prépare les données statistiques affichées dans dashboard.html.
    Chaque bloc est isolé pour éviter les crash si une table est vide.
    """
    # === Compteurs simples ===
    nb_clients = Client.query.count()
    nb_projets = Projet.query.count()
    nb_intervenants = Intervenant.query.count()

    # === Projets par statut ===
    statut_counts = {s.value: 0 for s in StatutProjet}
    projets_par_statut = (
        Projet.query.with_entities(Projet.statut_projet, func.count(Projet.id_projet))
        .group_by(Projet.statut_projet)
        .all()
    )
    for statut, count in projets_par_statut:
        statut_counts[statut.value] = count

    # === Disponibilité intervenants ===
    dispo_map = {"Disponible": 0, "Indisponible": 0}
    dispo_raw = (
        Intervenant.query.with_entities(Intervenant.disponible_actuellement, func.count())
        .group_by(Intervenant.disponible_actuellement)
        .all()
    )
    for dispo, count in dispo_raw:
        dispo_map["Disponible" if dispo else "Indisponible"] = count

    # === Interactions sur 6 mois ===
    labels, counts = [], []
    today = datetime.utcnow().date()
    for i in range(6, -1, -1):
        first = (today.replace(day=1) - timedelta(days=30*i)).replace(day=1)
        last = (first + timedelta(days=32)).replace(day=1) - timedelta(days=1)

        labels.append(first.strftime("%b %Y"))
        counts.append(
            InteractionClient.query.filter(
                InteractionClient.date_interaction >= first,
                InteractionClient.date_interaction <= last
            ).count()
        )

    return render_template(
        "dashboard.html",
        nb_clients=nb_clients,
        nb_projets=nb_projets,
        nb_intervenants=nb_intervenants,
        statut_counts=statut_counts,
        dispo_map=dispo_map,
        inter_labels=labels,
        inter_counts=counts
    )
