import os
from dotenv import load_dotenv
from app.models import db
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
