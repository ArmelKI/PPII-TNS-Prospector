import pytest
from datetime import date   
from app.models import db, Projet, Client, Convention, StatutProjet
from flask import url_for

def test_liste_projets_right_page(logged_in_client):
    response = logged_in_client.get("/projets/")
    assert response.status_code == 200
    assert "Projets" in response.get_data(as_text=True)

def test_ajouter_projet_is_right_page(logged_in_client):
    response = logged_in_client.get("/projets/add", follow_redirects=True)
    assert response.status_code == 200
    assert "Projet" in response.get_data(as_text=True) # redirection sur la page de détails

def test_ajouter_projet_post(admin_client, app):
    with app.app_context():
        client_test = Client.query.filter_by(mail_client="projet_test@mail.com").first()
        if not client_test:
            client_test = Client(
                id_client=None, # Laisser l'auto-increment si géré, sinon mettre un ID unique
                raison_sociale="Entreprise Projet",
                mail_client="projet_test@mail.com",
                telephone_client="0102030405",
                secteur="Test",
                date_dernier_contact=date.today(),
                latitude=48.8566,
                longitude=2.3522
            )
            db.session.add(client_test)
            db.session.commit()
        c_id = client_test.id_client

    response = admin_client.post(
        "/projets/add",
        data={
            "nom_projet": "Projet modal",
            "type_convention": "CC",
            "date_debut_projet": "2025-12-21",
            "prix": "700",
            "id_client": c_id
        },
        follow_redirects=True
    )
    assert response.status_code == 200
    with app.app_context():
        projet_db = Projet.query.filter_by(nom_projet="Projet modal").first()

def test_details_projet(logged_in_client, app):
    with app.app_context():
        c = Client(
            id_client=None,
            raison_sociale="Detail Corp",
            mail_client="detail@corp.com",
            telephone_client="0100000000",
            secteur="IT",
            date_dernier_contact=date.today(),
            latitude=0.0,
            longitude=0.0
        )
        db.session.add(c)
        db.session.flush()
        
        conv = Convention(id_client=c.id_client, type_convention="CC", date_debut_convention=date.today())
        db.session.add(conv)
        db.session.flush() 

        p = Projet(
            nom_projet="Projet Détail Test",
            id_convention=conv.id_convention,
            statut_projet=StatutProjet.PAS_COMMENCE
        )
        db.session.add(p)
        db.session.commit()
        p_id = p.id_projet
        target_url = url_for('projets.details_projet', id=p_id)
    
    response = logged_in_client.get(target_url)
    assert response.status_code == 200
    assert "Projet Détail Test" in response.get_data(as_text=True)