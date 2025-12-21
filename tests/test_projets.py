import pytest
from datetime import date   
from app.models import db, Projet

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

def test_ajouter_projet_duplicate(projet, app):
    pass

def test_details_projet(projet, app):
    pass

def test_details_projet_404(projet):
    pass

def test_modifier_projet_deadline_7_jan(projet):
    pass