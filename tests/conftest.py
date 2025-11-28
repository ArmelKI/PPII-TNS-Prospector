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

