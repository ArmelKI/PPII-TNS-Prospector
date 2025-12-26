import os
from dotenv import load_dotenv
from app.models import db, Utilisateur
import pytest
from app.__init__ import create_app

load_dotenv()

@pytest.fixture()
def app():
    db_password = os.getenv("DB_PASSWORD")
    os.environ["DB_NAME"] = "db_test"
    os.environ["DB_USER"] = "postgres"
    os.environ["DB_PASSWORD"] = db_password
    os.environ["DB_HOST"] = "localhost"
    os.environ["DB_PORT"] = "5432"

    app = create_app()
    app.config["TESTING"] = True

    with app.app_context():
        assert "test" in app.config["SQLALCHEMY_DATABASE_URI"]
        db.drop_all() # reproductibilité des tests
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def projet(app):
    return app.test_client()

from app.models import Utilisateur, Role, db  # Assure-toi d'importer Role

@pytest.fixture
def logged_in_client(client, app):
    with app.app_context():
        # 1. S'assurer que le rôle avec l'ID 1 existe
        role = Role.query.get(1)
        if not role:
            role = Role(id_role=1, nom_role="Admin") # Adapte selon tes colonnes
            db.session.add(role)
            db.session.commit()

        # 2. Création de l'utilisateur de test
        user = Utilisateur.query.filter_by(mail_utilisateur="test@test.com").first()
        if not user:
            user = Utilisateur(
                nom_utilisateur="Test",
                prenom_utilisateur="User",
                mail_utilisateur="test@test.com",
                mdp_utilisateur="password", 
                id_role=1
            )
            db.session.add(user)
            db.session.commit()
            
        # 3. Connexion (simulation du login)
        with client.session_transaction() as sess:
            sess['_user_id'] = str(user.id_utilisateur) # Flask-Login utilise souvent des strings
            sess['_fresh'] = True
            
        yield client
