"""
Tests for the /clients endpoint.
"""

from app.models import db, Client


def test_all_clients_empty(client):
    response = client.get("/clients")

    assert response.status_code == 200
    assert response.get_json() == []

def test_all_clients_entreprise_modale(client, app):

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

    resp = client.get("/clients")
    data = resp.get_json()  # retrieve the output returned by GET
    assert data == [{"raison_sociale": "Entreprise très modale"}]

def test_all_clients_returns_list(client):
    response = client.get("/clients")
    assert isinstance(response.get_json(), list)

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