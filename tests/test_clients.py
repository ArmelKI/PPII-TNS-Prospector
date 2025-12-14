"""
Tests for the /clients endpoint.
"""
import pytest
from datetime import date   
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

def test_ajouter_client_post_missing_field(client, app):
    with app.app_context():
        response = client.post(
            "/clients/add",
            data={
                "mail_client": "missing@test.com",
                "telephone_client": "0612345678",
                "secteur": "Test",
            },
            follow_redirects=True
        )
        html = response.get_data(as_text=True)
        assert response.status_code == 200
        assert "Nouveau Client" in html

def test_details_client(client, app):
    with app.app_context():
        new_client = Client(
            id_client=None,
            raison_sociale="Client Détail",
            mail_client="detail@test.com",
            telephone_client="0611111111",
            secteur="Test",
            date_dernier_contact=date.today(),
            latitude=0,
            longitude=0
        )
        db.session.add(new_client)
        db.session.commit()
        client_id = new_client.id_client

    response = client.get(f"/clients/{client_id}")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Client Détail" in html

def test_details_client_404(client):
    response = client.get("/clients/999999")  # ID non existant
    assert response.status_code == 404