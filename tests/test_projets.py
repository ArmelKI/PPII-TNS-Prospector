import pytest
from datetime import date   
from app.models import db, Projet, Client, Convention, StatutProjet
from flask import url_for

def test_liste_projets_right_page(projet):
    response = projet.get("/projets/")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Projets" in html

def test_ajouter_projet_is_right_page(projet):
    response = projet.get("/projets/add")

    assert response.status_code == 200
    html = response.get_data(as_text=True)

    assert "Nouveau Projet" in html

def test_ajouter_projet_post(client, projet, app):
    client.post(
        "/clients/add",
        data={
            "raison_sociale": "Entreprise modale",
            "mail_client": "entreprise@modale.com",
            "telephone_client": "77777777",
            "secteur": "Statistiques",
            "id_client":1
        },
        follow_redirects=True
    )
    response = projet.post(
        "/projets/add",
        data={
            "nom_projet": "Projet modal",
            "type_convention": "CC",
            "date_debut_projet": "2025-12-21",
            "prix": "7",
            "id_client":1
        },
        follow_redirects=True
    )
    assert response.status_code == 200
    with app.app_context():
        projet_db = Projet.query.filter_by(
            nom_projet="Projet modal"
        ).first()

        assert projet_db is not None
        assert projet_db.date_debut_projet == date(2025, 12, 21)

def test_ajouter_projet_post_missing_field(client, projet, app):
    client.post(
        "/clients/add",
        data={
            "raison_sociale": "Entreprise modale",
            "mail_client": "entreprise@modale.com",
            "telephone_client": "77777777",
            "secteur": "Statistiques",
            "id_client":1
        },
        follow_redirects=True
    )
    with app.app_context():
        nb_projets_avant = Projet.query.count()
        response = projet.post(
            "/projets/add",
            data={
                "type_convention": "CC",
                "date_debut_projet": "2025-12-21",
                "id_client":1
            },
            follow_redirects=True
        )
        html = response.get_data(as_text=True)
        assert response.status_code == 200
        assert "Nouveau Projet" in html
        assert Projet.query.count() == nb_projets_avant

def test_ajouter_projet_duplicate(client, projet, app):
    data = {
        "nom_projet": "Projet modal",
        "type_convention": "CC",
        "id_client": 1,
        "date_debut_projet": "2025-12-21",
    }
    client.post(
        "/clients/add",
        data={
            "raison_sociale": "Entreprise modale",
            "mail_client": "entreprise@modale.com",
            "telephone_client": "77777777",
            "secteur": "Statistiques",
            "id_client":1
        },
        follow_redirects=True
    )
    projet.post("/projets/add", data=data, follow_redirects=True)
    with app.app_context():
        projet_in_db = Projet.query.filter_by(nom_projet="Projet modal").all()
        assert len(projet_in_db) == 1 
    projet.post("/clients/add", data=data, follow_redirects=True)
    with app.app_context():
        projet_in_db = Projet.query.filter_by(nom_projet="Projet modal").all()
        assert len(projet_in_db) == 1

def test_details_projet(projet, app):
    with app.app_context():
        client_test = Client(
            raison_sociale="Client Test",
            mail_client="test@test.com",
            secteur="IT",
            date_dernier_contact="2025-12-21",
            telephone_client="77777777",
            latitude="777.7777777",
            longitude="777.7777777",
            id_client=1
        )
        db.session.add(client_test)
        
        new_conv = Convention(
            id_client=1,
            type_convention="CC",
            date_debut_convention=date.today()
        )
        db.session.add(new_conv)
        db.session.flush() 

        new_projet = Projet(
            nom_projet="Projet Détail Test",
            id_convention=new_conv.id_convention,
            statut_projet=StatutProjet.PAS_COMMENCE
        )
        db.session.add(new_projet)
        db.session.commit()
        projet_id = new_projet.id_projet
        target_url = url_for('projets.details_projet', id=projet_id)
    
    response = projet.get(target_url)
    
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Projet Détail Test" in html

def test_details_projet_404(projet):
    pass

def test_modifier_projet_deadline_7_jan(projet):
    pass