import pytest
import io
from app.models import Role, Utilisateur, db

@pytest.fixture
def base_setup(app):
    with app.app_context():
        # Nécessaire pour les clés étrangères
        role_admin = Role(id_role=1, nom_role="Admin")
        db.session.add(role_admin)
        db.session.commit()
        yield