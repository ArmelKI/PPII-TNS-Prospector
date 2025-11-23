import pytest
from app import create_app
from app.models import db as _db

@pytest.fixture
def app():
    # Pass test config into create_app so DB URI is set early and create_all() is disabled
    config = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "AUTO_CREATE_DB": False,  # disable auto create in factory
        "WTF_CSRF_ENABLED": False
    }

    app = create_app(test_config=config)

    # Now create tables explicitly inside the test context using the sqlite test DB
    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()
