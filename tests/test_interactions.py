from app.models import InteractionClient, Client, EtatRelation, db
from datetime import date, timedelta
import pytest

def test_liste_interactions_display(client, app):
    """Vérifie l'affichage de la liste des interactions."""
    with app.app_context():
        etat = EtatRelation(id_etat_relation=1, libelle_relation="Prospect")
        nouveau_client = Client(
            id_client=1,
            raison_sociale="Ma Super Entreprise",
            mail_client="test@test.com",
            telephone_client="0102030405",
            secteur="Informatique",
            date_dernier_contact=date.today(),
            latitude=48.8566,
            longitude=2.3522
        )
        db.session.add_all([etat, nouveau_client])
        db.session.commit()

        inter = InteractionClient(
            id_client=1,
            date_interaction=date.today(),
            detail_interaction="Appel de prospection",
            id_etat_relation=1
        )
        db.session.add(inter)
        db.session.commit()

    response = client.get("/interactions/")
    assert response.status_code == 200
    assert b"Appel de prospection" in response.data

def test_liste_interactions_sorting(client, app):
    """Vérifie que les interactions sont triées par date décroissante (plus récent en haut)."""
    with app.app_context():
        etat = EtatRelation(id_etat_relation=1, libelle_relation="Suivi")
        client_test = Client(1, "Entreprise Tri", None, None, None, None, None, None)
        db.session.add_all([etat, client_test])
        db.session.commit()

        date_recent = date.today()
        date_ancien = date.today() - timedelta(days=5)

        inter_ancien = InteractionClient(
            id_client=1, 
            detail_interaction="Interaction Ancienne", 
            date_interaction=date_ancien,
            id_etat_relation=1
        )
        inter_recent = InteractionClient(
            id_client=1, 
            detail_interaction="Interaction Recente", 
            date_interaction=date_recent,
            id_etat_relation=1
        )
        
        db.session.add_all([inter_ancien, inter_recent])
        db.session.commit()

    response = client.get("/interactions/")
    assert response.status_code == 200
    
    html = response.data.decode()
    index_recent = html.find("Interaction Recente")
    index_ancien = html.find("Interaction Ancienne")
    
    assert index_recent != -1, "L'interaction récente n'est pas affichée"
    assert index_ancien != -1, "L'interaction ancienne n'est pas affichée"
    assert index_recent < index_ancien, "Le tri décroissant n'est pas respecté"