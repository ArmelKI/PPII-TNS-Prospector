import pytest
from app.models import Client, db
from datetime import date, datetime

@pytest.fixture
def setup_client_100(app):
    """Prépare un client proprement."""
    with app.app_context():
        # Nettoyage préventif
        Client.query.filter_by(id_client=100).delete()
        db.session.commit()
            
        client_obj = Client(
            id_client=100,
            raison_sociale="API Corp",
            mail_client="contact@api.com",
            telephone_client="0123456789",
            secteur="Tech",
            # CORRECTION ICI : Utilisation d'un objet date
            date_dernier_contact=None, 
            latitude=48.85,
            longitude=2.35
        )
        db.session.add(client_obj)
        db.session.commit()
        
        yield client_obj.id_client 
        
        with app.app_context():
            db.session.query(Client).filter_by(id_client=100).delete()
            db.session.commit()

@pytest.fixture
def client_pour_changement_id(app):
    """Fixture qui crée un client avec l'ID 50 et nettoie après le test."""
    with app.app_context():
        db.session.query(Client).filter(Client.id_client.in_([50, 60])).delete()
        
        c = Client(
            id_client=50, 
            raison_sociale="Initial",
            mail_client="test@test.com",
            telephone_client="00000000",
            secteur="Test",
            date_dernier_contact=None,
            latitude=0.0,
            longitude=0.0
        )
        db.session.add(c)
        db.session.commit()
        yield c 
        
        with app.app_context():
            db.session.query(Client).filter(Client.id_client.in_([50, 60])).delete()
            db.session.commit()

# --- TESTS UNITAIRES (AUTHENTIFIÉS) ---

def test_api_create_client(logged_in_client, app):
    """Teste la création d'un client via POST."""
    payload = {
        "id_client": 200,
        "raison_sociale": "New Corp",
        "mail_client": "new@corp.com",
        "telephone_client": "00000000",
        "secteur": "Finance",
        "date_dernier_contact": None,
        "latitude": 0.0,
        "longitude": 0.0
    }
    # Utilisation de logged_in_client au lieu de client
    response = logged_in_client.post("/api/clients", json=payload)
    assert response.status_code == 200
    
    with app.app_context():
        assert Client.query.get(200) is not None

def test_api_get_all_clients(logged_in_client, setup_client_100):
    """Teste la récupération de la liste complète."""
    response = logged_in_client.get("/api/clients/get_all")
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert any(c['id_client'] == 100 for c in response.json)

def test_api_get_single_client(logged_in_client, setup_client_100):
    """Teste la récupération d'un client spécifique par ID."""
    response = logged_in_client.get("/api/clients?id=100")
    assert response.status_code == 200
    assert response.json["id_client"] == 100
    assert response.json["raison_sociale"] == "API Corp"

def test_api_update_client_success(logged_in_client, setup_client_100, app):
    """Utilise l'ID passé par la fixture."""
    client_id = setup_client_100
    payload = {
        "id_client": client_id, 
        "raison_sociale": "API Limited"
    }
    response = logged_in_client.put(f"/api/clients?id={client_id}", json=payload)
    
    assert response.status_code == 200
    
    with app.app_context():
        # IMPORTANT: expire_all() force SQLA à recharger les données de la DB
        db.session.expire_all()
        c = db.session.get(Client, client_id)
        assert c.raison_sociale == "API Limited"

def test_api_delete_client(logged_in_client, setup_client_100, app):
    """Teste la suppression d'un client."""
    response = logged_in_client.delete("/api/clients?id=100")
    assert response.status_code == 200
    assert "deleted" in response.json["message"]
    
    with app.app_context():
        assert Client.query.get(100) is None

def test_api_client_not_found(logged_in_client):
    """Vérifie que l'API renvoie 404 si l'ID n'existe pas."""
    response = logged_in_client.get("/api/clients?id=9999")
    # Maintenant que nous sommes loggés, nous devrions recevoir 404 et non 302
    assert response.status_code == 404

def test_api_put_client_id_mismatch_blocks_without_confirm(logged_in_client, client_pour_changement_id):
    """Vérifie que le changement d'ID est bloqué sans confirmation."""
    payload = {
        "id_client": 60, 
        "raison_sociale": "Tentative Changement"
    }
    response = logged_in_client.put("/api/clients?id=50", json=payload)
    
    assert response.status_code == 200
    assert response.json["message"] == "client IDs not matching, confirmation needed !"

def test_api_put_client_id_change_success_with_confirm(logged_in_client, client_pour_changement_id, app):
    """Vérifie que le changement d'ID réussit avec le paramètre de confirmation."""
    payload = {
        "id_client": 60, 
        "raison_sociale": "Changement Confirmé",
        "mail_client": "test@test.com",
        "telephone_client": "00000000",
        "secteur": "Test",
        "date_dernier_contact": None,
        "latitude": 0.0,
        "longitude": 0.0
    }
    
    response = logged_in_client.put("/api/clients?id=50&confirm_change_id=true", json=payload)
    
    assert response.status_code == 200
    assert response.json["message"] == "Client updated"
    
    with app.app_context():
        assert Client.query.get(60) is not None
        assert Client.query.get(50) is None