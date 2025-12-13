import os
from dotenv import load_dotenv
from urllib.parse import quote_plus  # Use quote_plus for URL encoding strings
from app.models import db
import pytest
from app.__init__ import create_app

load_dotenv()

@pytest.fixture()
def app():
    # Get the database password from environment variables and URL-encode it
    db_password = os.getenv("DB_PASSWORD")
    if db_password is not None:
        db_password = quote_plus(db_password)
    else:
        db_password = ""

    # Set environment variables for the test database
    os.environ["DB_NAME"] = "db_test"
    os.environ["DB_USER"] = "postgres"
    os.environ["DB_PASSWORD"] = db_password
    os.environ["DB_HOST"] = "localhost"
    os.environ["DB_PORT"] = "5432"

    app = create_app()
    app.config["TESTING"] = True

    # Create a new database schema for testing
    with app.app_context():
        db.drop_all()
        db.create_all()

    yield app
    # Using yield makes this fixture a generator, so the code after yield will run after the test

@pytest.fixture
def client(app):
    # Returns a test client for making HTTP requests without running the server
    return app.test_client()
