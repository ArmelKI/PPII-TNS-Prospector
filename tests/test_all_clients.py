import json
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
            mail_client = "entreprise@test.ts",
            telephone_client = "7777777",
            secteur = "modalite",
            date_dernier_contact = "2024-02-01",
            latitude = 777.7777777,
            longitude = 777.7777777)
        db.session.add(c) # on crée un client qu'on ajoute à la base de test pour s'assurer que tout marche bien
        db.session.commit()

    resp = client.get("/clients")
    data = resp.get_json() # récupère l'output donné par GET
    assert data == [{"raison_sociale":"Entreprise très modale"}]

def test_all_clients_returns_list(client):
    response = client.get("/clients")
    assert isinstance(response.get_json(), list)