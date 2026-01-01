import pytest
from unittest.mock import patch
from app.models import Client, db

def test_map_page_access(logged_in_client):
    """Vérifie que la page HTML de la carte est accessible."""
    response = logged_in_client.get("/map/")
    assert response.status_code == 200
    assert b"map" in response.data # Vérifie la présence de contenu lié à la map

def test_clients_api_empty(logged_in_client):
    """Vérifie que l'API retourne une liste vide quand il n'y a pas de clients."""
    response = logged_in_client.get("/map/api")
    assert response.status_code == 200
    assert response.get_json() == []

def test_clients_api_with_data(app, logged_in_client):
    """Vérifie que l'API retourne les clients présents en base."""
    with app.app_context():
        c = Client(
            id_client=None, # ou une valeur entière si requis
            raison_sociale="Entreprise A",
            mail_client=None,
            telephone_client=None,
            date_dernier_contact=None,
            secteur="BTP",
            latitude=48.0,
            longitude=6.0
        )
        db.session.add(c)
        db.session.commit()

    response = logged_in_client.get("/map/api")
    data = response.get_json()
    
    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]["name"] == "Entreprise A"

### 2. Tests de la route Overpass (Mocks)
@patch("requests.post")
def test_prospects_api_success(mock_post, logged_in_client):
    """Simule une réponse réussie de l'API Overpass."""
    # Simulation du retour de l'API externe
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {
        "elements": [
            {
                "lat": 48.6, "lon": 6.1,
                "tags": {"name": "Nouveau Prospect", "shop": "bakery"}
            }
        ]
    }

    response = logged_in_client.get("/map/1000")
    data = response.get_json()

    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]["name"] == "Nouveau Prospect"
    assert data[0]["type"] == "bakery"

### 3. Tests d'ajout de prospect
def test_add_prospect_success(app, logged_in_client):
    """Vérifie l'ajout correct d'un prospect en base."""
    payload = {
        "lat": 49.0,
        "lng": 2.0,
        "name": "Nouveau Client Test",
        "type": "Informatique"
    }
    response = logged_in_client.post("/map/add_prospect", json=payload)
    
    assert response.status_code == 200
    assert response.get_json()["success"] is True

    with app.app_context():
        client_in_db = Client.query.filter_by(raison_sociale="Nouveau Client Test").first()
        assert client_in_db is not None

def test_add_prospect_missing_data(logged_in_client):
    """Vérifie l'erreur si des données sont manquantes."""
    payload = {"lat": 49.0} # Manque nom, lng, type
    response = logged_in_client.post("/map/add_prospect", json=payload)
    
    assert response.status_code == 400
    assert "Données manquantes" in response.get_json()["message"]

def test_add_prospect_already_exists(app, logged_in_client):
    """Vérifie qu'on ne crée pas de doublon."""
    client_data = {"lat": 45.0, "lng": 5.0, "name": "Doublon", "type": "Test"}
    
    # Premier ajout
    logged_in_client.post("/map/add_prospect", json=client_data)
    # Deuxième ajout identique
    response = logged_in_client.post("/map/add_prospect", json=client_data)
    
    assert response.status_code == 200
    assert "Client déjà présent" in response.get_json()["message"]

### 4. Tests de suppression
def test_delete_client_success(app, logged_in_client):
    """Vérifie la suppression d'un client."""
    with app.app_context():
        c = Client(
            id_client=None,
            raison_sociale="A supprimer",
            mail_client=None,
            telephone_client=None,
            date_dernier_contact=None,
            secteur="Test",
            latitude=0.0,
            longitude=0.0
        )
        db.session.add(c)
        db.session.commit()
        client_id = c.id_client

    response = logged_in_client.delete(f"/map/delete_client/{client_id}")
    assert response.status_code == 200
    assert response.get_json()["success"] is True

    with app.app_context():
        assert Client.query.get(client_id) is None

def test_delete_client_not_found(logged_in_client):
    """Vérifie l'erreur 404 si le client n'existe pas."""
    response = logged_in_client.delete("/map/delete_client/9999")
    assert response.status_code == 404