"""
Tests for the /clients endpoint.
"""
import pytest
from app.models import db, Client

def test_liste_clients_empty(client):
    response = client.get("/clients/")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Clients" in html

def test_ajouter_client_is_right_page(client):
    response = client.get("/clients/add")

    assert response.status_code == 200
    html = response.get_data(as_text=True)

    assert "Nouveau Client" in html

def test_ajouter_client_post(client, app):
    response = client.post(
        "/clients/add",
        data={
            "raison_sociale": "Entreprise modale",
            "mail_client": "entreprise@modale.com",
            "telephone_client": "77777777",
            "secteur": "Statistiques",
        },
        follow_redirects=True
    )
    assert response.status_code == 200
    with app.app_context():
        client_db = Client.query.filter_by(
            raison_sociale="Entreprise modale"
        ).first()

        assert client_db is not None
        assert client_db.mail_client == "entreprise@modale.com"

def test_all_clients_right_keys(client, app):
    with app.app_context():
        c = Client(
            id_client=0,
            raison_sociale="Entreprise très modale",
            mail_client="entreprise@test.ts",
            telephone_client="7777777",
            secteur="modalite",
            date_dernier_contact="2024-02-01",
            latitude=777.7777777,
            longitude=777.7777777)
        db.session.add(c)  # create a client and add it to the test database to ensure it's working
        db.session.commit()

    data = client.get("/clients").get_json()
    assert list(data[0].keys()) == ["raison_sociale"]  # modify when other client info should be displayed