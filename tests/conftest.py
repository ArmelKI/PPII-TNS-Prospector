import os
from dotenv import load_dotenv
import pytest
from app.__init__ import create_app
from app.models import db, Utilisateur, Role

load_dotenv()

@pytest.fixture()
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///test_prospector.db", # Base de données ultra-rapide
        "SQLALCHEMY_TRACK_MODIFICATIONS": False
    })

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def logged_in_client(client, app):
    with app.app_context():
        # S'assurer que le rôle par défaut existe
        if not db.session.get(Role, 1):
            role = Role(id_role=1, nom_role="Admin")
            db.session.add(role)
            db.session.commit()

        # Création de l'utilisateur de test
        user = Utilisateur(
            nom_utilisateur="Test",
            prenom_utilisateur="User",
            mail_utilisateur="test@test.com",
            id_role=1
        )
        user.set_password("password")
        db.session.add(user)
        db.session.commit()
            
        # Simulation de session Flask-Login
        with client.session_transaction() as sess:
            sess['_user_id'] = str(user.id_utilisateur)
            sess['_fresh'] = True
            
        yield client