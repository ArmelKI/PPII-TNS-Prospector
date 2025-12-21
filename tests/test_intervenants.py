import pytest
import io
from app.models import Role, Utilisateur, db, Intervenant

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