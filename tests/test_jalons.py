import pytest
from app.models import db, Projet, Jalon, StatutJalon, Convention

from app.models import db, Projet, Jalon, StatutJalon, Convention, Client # Assurez-vous d'importer Client

from datetime import date
from app.models import db, Projet, Jalon, StatutJalon, Convention, Client, StatutProjet

@pytest.fixture
def setup_projet_data(app):
    """Crée l'arborescence complète nécessaire aux tests."""
    with app.app_context():
        # 1. Créer le Client (tous les arguments de votre __init__ sont requis)
        client = Client(
            id_client=1,
            raison_sociale="Client Test",
            mail_client="test@client.com",
            telephone_client="0102030405",
            secteur="Informatique",
            date_dernier_contact=date.today(),
            latitude=48.8566,
            longitude=2.3522
        )
        db.session.add(client)
        db.session.flush()

        # 2. Créer la Convention (respecter le CheckConstraint 'CE' ou 'CC')
        convention = Convention(
            id_client=client.id_client,
            type_convention="CE",  # 'CE' ou 'CC' uniquement
            date_debut_convention=date.today(),
            prix=1000.00
        )
        db.session.add(convention)
        db.session.flush()

        # 3. Créer le Projet
        projet = Projet(
            nom_projet="Projet Kanban Test",
            id_convention=convention.id_convention,
            statut_projet=StatutProjet.EN_COURS
        )
        db.session.add(projet)
        db.session.flush()

        # 4. Créer le Jalon
        jalon = Jalon(
            nom_jalon="Jalon initial",
            id_projet=projet.id_projet,
            statut_jalon=StatutJalon.ACTUEL, # StatutJalon utilise A_VENIR, ACTUEL, PASSE
            date_debut_jalon=date.today()
        )
        db.session.add(jalon)
        db.session.commit()
        
        return projet.id_projet, jalon.id_jalon

def test_voir_kanban_success(logged_in_client, setup_projet_data):
    """Vérifie que la page Kanban s'affiche correctement pour un projet existant."""
    id_projet, _ = setup_projet_data
    response = logged_in_client.get(f"/jalons/kanban/{id_projet}")
    
    assert response.status_code == 200
    assert b"Projet Kanban Test" in response.data
    assert b"Jalon initial" in response.data

def test_voir_kanban_404(logged_in_client):
    """Vérifie qu'un projet inexistant renvoie une erreur 404."""
    response = logged_in_client.get("/jalons/kanban/999")
    assert response.status_code == 404

def test_api_update_statut_success(logged_in_client, setup_projet_data):
    """Vérifie la mise à jour du statut d'un jalon via l'API."""
    _, id_jalon = setup_projet_data
    
    # On change le statut de 'ACTUEL' (mis dans la fixture) à 'PASSE'
    response = logged_in_client.post("/jalons/api/update_statut", json={
        "id_jalon": id_jalon,
        "nouveau_statut": "Passé" # Doit correspondre à StatutJalon.PASSE.value
    })
    
    assert response.status_code == 200
    assert response.get_json()["success"] is True

    # Vérification en base de données
    with logged_in_client.application.app_context():
        # Utilisation de db.session.get (recommandé pour SQLAlchemy 2.0)
        jalon = db.session.get(Jalon, id_jalon)
        assert jalon.statut_jalon == StatutJalon.PASSE

def test_api_update_statut_invalid(logged_in_client, setup_projet_data):
    """Vérifie qu'un statut inconnu renvoie une erreur 400."""
    _, id_jalon = setup_projet_data
    
    response = logged_in_client.post("/jalons/api/update_statut", json={
        "id_jalon": id_jalon,
        "nouveau_statut": "STATUT_INEXISTANT"
    })
    
    assert response.status_code == 400
    data = response.get_json()
    assert data["success"] is False
    assert data["error"] == "Unknown status"

def test_api_update_statut_404(logged_in_client):
    """Vérifie la mise à jour d'un jalon qui n'existe pas."""
    response = logged_in_client.post("/jalons/api/update_statut", json={
        "id_jalon": 999,
        "nouveau_statut": "Passé" # Utilisation d'un statut valide pour isoler l'erreur 404
    })
    assert response.status_code == 404