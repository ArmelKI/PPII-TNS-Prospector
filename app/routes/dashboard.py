# app/routes/dashboard.py
"""
Blueprint dashboard — lecture sûre des données pour le tableau de bord.

Raison : certaines valeurs en base peuvent ne pas correspondre exactement
aux valeurs de l'Enum Python (StatutProjet). Pour éviter un crash 500,
on récupère les statuts depuis la base en texte brut via une requête SQL
et on reconstruit un comptage robuste côté application.
"""

from flask import Blueprint, render_template, current_app
from app.models import Client, Projet, Intervenant, InteractionClient, StatutProjet
from sqlalchemy import func, text
from datetime import datetime, timedelta
from app.models import db

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
def dashboard():
    # compteurs simples
    nb_clients = Client.query.count()
    nb_projets = Projet.query.count()
    nb_intervenants = Intervenant.query.count()

    # --- Projets par statut : récupération robuste via SQL pour éviter les erreurs Enum ---
    # On récupère les valeurs brutes (texte) et on les convertit côté Python.
    statut_counts = {s.value: 0 for s in StatutProjet}

# TODO enlever le sql
    try:
        # Requête SQL qui renvoie le statut tel qu'il est en base (string) et le compte
        sql = text("SELECT statut_projet, COUNT(id_projet) AS cnt FROM projets GROUP BY statut_projet")
        rows = db.session.execute(sql).all()
    except Exception as e:
        # En cas d'erreur d'exécution (ex : table inexistante), on met tout à 0
        current_app.logger.exception("Erreur lors de la récupération des projets par statut")
        rows = []

# TODO y'a surement plus simple (c'était pour le graphe)
    # rows contient des tuples (statut_value_from_db, cnt)
    unknown_values = []
    for raw_statut, cnt in rows:
        # raw_statut peut être None, bytes, enum, ou str selon la DB/drivers
        if raw_statut is None:
            label = "Non défini"
            statut_counts.setdefault(label, 0)
            statut_counts[label] += cnt
            continue

        # forcer en str
        raw_label = str(raw_statut)

        # essayer de trouver le statut correspondant dans l'enum
        matched = False
        for s in StatutProjet:
            if raw_label == s.value:
                statut_counts[s.value] += cnt
                matched = True
                break

        if not matched:
            # valeur inconnue : on l'ajoute sous sa propre étiquette pour la visibilité
            statut_counts.setdefault(raw_label, 0)
            statut_counts[raw_label] += cnt
            unknown_values.append(raw_label)

    if unknown_values:
        # log pour information : tu pourras corriger en base ensuite
        current_app.logger.warning("Valeurs inconnues pour Projet.statut_projet trouvées en DB: %s", list(set(unknown_values)))

    # --- Disponibilité intervenants ---
    dispo_map = {"Disponible": 0, "Indisponible": 0}
    dispo_raw = (
        Intervenant.query.with_entities(Intervenant.disponible_actuellement, func.count())
        .group_by(Intervenant.disponible_actuellement)
        .all()
    )
    for dispo, cnt in dispo_raw:
        dispo_map["Disponible" if dispo else "Indisponible"] = cnt

    # --- Interactions sur 6 derniers mois ---
    labels, counts = [], []
    # use timezone-naive date (compatible avec tests existants)
    today = datetime.utcnow().date()
    for i in range(6, -1, -1):
        ref = (today.replace(day=1) - timedelta(days=30 * i)).replace(day=1)
        start = ref
        end = (ref + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        labels.append(start.strftime("%b %Y"))
        cnt = InteractionClient.query.filter(
            InteractionClient.date_interaction >= start,
            InteractionClient.date_interaction <= end
        ).count()
        counts.append(cnt)

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
