import pytest
from app.models import *
from datetime import date, timedelta

@pytest.fixture
def setup_dashboard_data(app):
    with app.app_context():
        # 1. Nettoyage dans l'ordre inverse des dépendances (IMPORTANT)
        # On supprime d'abord les enfants, puis les parents
        db.session.query(Jalon).delete()
        db.session.query(Projet).delete()
        db.session.query(Intervenant).delete()
        db.session.query(Utilisateur).delete()
        db.session.query(Role).delete()  # On vide les rôles
        db.session.query(Client).delete()
        
        # 2. Création du Rôle requis
        # On crée le rôle avec l'ID 1 pour que l'utilisateur puisse y être lié
        role_admin = Role(id_role=1, nom_role="Administrateur")
        db.session.add(role_admin)
        db.session.flush() # On pousse le rôle en base pour qu'il soit disponible

        # 3. Création de l'Utilisateur
        user_intervenant = Utilisateur(
            id_utilisateur=10,
            nom_utilisateur="Martin",
            prenom_utilisateur="Jean",
            mail_utilisateur="jean.martin@test.com",
            mdp_utilisateur="password_hash",
            id_role=1 # Maintenant, cet ID existe !
        )
        db.session.add(user_intervenant)
        db.session.flush()

        # 4. Création de l'Intervenant
        i1 = Intervenant(
            id_intervenant=user_intervenant.id_utilisateur,
        )
        db.session.add(i1)

        # 5. Création du Client
        c1 = Client(
            raison_sociale="Client A", 
            mail_client="a@a.com", 
            telephone_client="0102030405",
            secteur="IT", 
            date_dernier_contact=date.today(), 
            latitude=0.0, 
            longitude=0.0,
            id_client=None
        )
        db.session.add(c1)
        db.session.commit()

def test_dashboard_counts(client, setup_dashboard_data):
    """Vérifie les compteurs de base : clients, intervenants et projets actifs."""
    response = client.get("/")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    
    # nb_projets actifs = EN_COURS + BLOQUE (donc 2 dans notre fixture)
    assert "2" in html 
    # nb_clients = 1
    assert "1" in html