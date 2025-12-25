import pytest
import io
from app.models import Role, Utilisateur, db, Intervenant
from flask import get_flashed_messages

@pytest.fixture
def base_setup(app):
    with app.app_context():
        role_admin = Role(id_role=1, nom_role="Admin")
        db.session.add(role_admin)
        db.session.commit()
        yield

def test_liste_intervenants_filters(client, app, base_setup):
    """Vérifie que la recherche par nom et le filtre dispo fonctionnent."""
    with app.app_context():
        # Création d'un utilisateur et son profil intervenant
        u = Utilisateur(id_utilisateur=10, nom_utilisateur="Zola", prenom_utilisateur="Emile", 
                        mail_utilisateur="emile@test.com", mdp_utilisateur="pwd", id_role=1)
        i = Intervenant(id_intervenant=10, disponible=True, nb_heures_dispo=10)
        db.session.add_all([u, i])
        db.session.commit()

    # Test recherche
    response = client.get("/intervenants/?search=Zola")
    assert b"Zola" in response.data

    # Test filtre disponibilité
    response_dispo = client.get("/intervenants/?disponibilite=disponible")
    assert b"Zola" in response_dispo.data

def test_ajouter_intervenant_fichiers_manquants(client, app):
    """Vérifie que l'erreur est bien générée dans la session Flask."""
    data = {
        "nom_utilisateur": "Hugo",
        "prenom_utilisateur": "Victor",
        "email_utilisateur": "victor@hugo.com"
    }
    
    # On utilise le gestionnaire de contexte pour intercepter les messages flash
    with client:
        response = client.post(
            "/intervenants/add", 
            data=data, 
            content_type='multipart/form-data', 
            follow_redirects=True
        )
        
        # On vérifie directement dans les messages flash de la session
        messages = get_flashed_messages(with_categories=True)
        assert any("Le CV est obligatoire" in msg for cat, msg in messages)
        assert response.status_code == 200