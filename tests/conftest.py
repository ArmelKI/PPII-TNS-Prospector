import sys, pathlib, os
from dotenv import load_dotenv
from urllib.parse import quote
from app.models import db
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pytest
from app.__init__ import create_app

load_dotenv()

@pytest.fixture()
def app():
    DB_PASSWORD = quote(os.getenv("DB_PASSWORD"))
    os.environ["DB_NAME"] = "db_test"
    os.environ["DB_USER"] = "postgres"
    os.environ["DB_PASSWORD"] = DB_PASSWORD
    os.environ["DB_HOST"] = "localhost"
    os.environ["DB_PORT"] = "5432"

    app = create_app()
    app.config["TESTING"] = True

    with app.app_context():
        db.drop_all()
        db.create_all()

    yield app
    # transforme app() en intérable (un truc sur lequel on peut faire une boucle for)
    # ça n'arrête pas la fonction contrairement au return

@pytest.fixture
def client(app):
    return app.test_client()  # test_client() permet de faire les fameuses requêtes HTTP sans lancer de serveur !
