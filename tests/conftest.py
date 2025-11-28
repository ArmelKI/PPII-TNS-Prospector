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
    })

    yield app
    # transforme app() en intérable (un truc sur lequel on peut faire une boucle for)
    # ça n'arrête pas la fonction contrairement au return

@pytest.fixture()
def client(app):
    return app.test_client() # test_client() permet de faire les fameuses requêtes HTTP sans lancer de serveur !

@pytest.fixture()
def runner(app):
    return app.test_cli_runner() 
    # en gros, imite la ligne de commande pour pouvoir passer des commandes dans de futurs tests