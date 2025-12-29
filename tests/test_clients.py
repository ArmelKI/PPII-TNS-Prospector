"""
Tests pour la route client (Interface Web)
"""
import pytest
from datetime import date   
from app.models import db, Client

def test_liste_clients_empty(logged_in_client):
    """Vérifie l'accès à la liste des clients."""
    response = logged_in_client.get("/clients/")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Clients" in html

def test_ajouter_client_is_right_page(logged_in_client):
    """Vérifie l'affichage du formulaire d'ajout."""
    response = logged_in_client.get("/clients/add")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Nouveau Client" in html

def test_ajouter_client_post(logged_in_client, app):
    """Teste la création d'un client via le formulaire (POST)."""
    response = logged_in_client.post(
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

def test_ajouter_client_post_missing_field(logged_in_client, app):
    """Vérifie qu'un champ manquant recharge le formulaire (ou affiche une erreur)."""
    response = logged_in_client.post(
        "/clients/add",
        data={
            "mail_client": "missing@test.com",
            "telephone_client": "0612345678",
            "secteur": "Test",
            # "raison_sociale" manquant
        },
        follow_redirects=True
    )
    html = response.get_data(as_text=True)
    assert response.status_code == 200
    # Si le champ manque, on reste généralement sur la page "Nouveau Client"
    assert "Nouveau Client" in html

def test_ajouter_client_duplicate(logged_in_client, app):
    """Vérifie que les doublons de raison sociale sont gérés."""
    data = {
        "raison_sociale": "Entreprise Unique",
        "mail_client": "dup@test.com",
        "telephone_client": "0123456789",
        "secteur": "Test",
    }

    # Premier ajout
    logged_in_client.post("/clients/add", data=data, follow_redirects=True)
    
    # Tentative de deuxième ajout
    logged_in_client.post("/clients/add", data=data, follow_redirects=True)
    
    with app.app_context():
        clients_in_db = Client.query.filter_by(raison_sociale="Entreprise Unique").all()
        # On vérifie qu'il n'y en a qu'un seul en base
        assert len(clients_in_db) == 1

def test_details_client(logged_in_client, app):
    """Teste l'affichage de la fiche détaillée d'un client."""
    with app.app_context():
        # Ajout de id_client=None pour satisfaire le constructeur du modèle
        new_client = Client(
            id_client=None,  # <--- Correction ici
            raison_sociale="Client Détail",
            mail_client="detail@test.com",
            telephone_client="0611111111",
            secteur="Test",
            date_dernier_contact=date.today(),
            latitude=0.0,
            longitude=0.0
        )
        db.session.add(new_client)
        db.session.commit()
        # On récupère l'ID généré par la base de données
        client_id = new_client.id_client

    response = logged_in_client.get(f"/clients/{client_id}")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Client Détail" in html

def test_details_client_404(logged_in_client):
    """Vérifie qu'un ID inconnu renvoie bien une 404 (et non une redirection)."""
    response = logged_in_client.get("/clients/999999") 
    assert response.status_code == 404