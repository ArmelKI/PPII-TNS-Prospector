import sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pytest
from app.__init__ import create_app

@pytest.fixture()
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })

    yield app
    # transforme app() en intérable (un truc sur lequel on peut faire une boucle for)
    # ça n'arrête pas la fonction contrairement au return

@pytest.fixture(autouse=True)
def clean_db(app):
    """
    Crée une DB propre à chaque test.
    Cette DB est créée au début du test et supprimée après celui-ci.

    S'exécute lors de chaque test (voir autouse)
    """
    from app.models import db

    with app.app_context():
        db.create_all()

    # avant le test, s'exécute le code ci-dessus
    # le yield balance la fonction au test qui s'exécute à son tour
    yield
    # quand le test est terminé, le code ci-dessous est exécuté

    with app.app_context():
        db.session.remove()
        db.drop_all()

@pytest.fixture()
def client(app):
    return app.test_client() # test_client() permet de faire les fameuses requêtes HTTP sans lancer de serveur !

@pytest.fixture()
def runner(app):
    return app.test_cli_runner()
    # en gros, imite la ligne de commande pour pouvoir passer des commandes dans de futurs tests