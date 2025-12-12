"""
app.__init__ — Factory for the TNS application (test-friendly version)

- Accepts an optional `test_config` dictionary to override app.config before initializing the database.
- Uses the `AUTO_CREATE_DB` config key to control whether to call db.create_all().
    For tests, set {"AUTO_CREATE_DB": False, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"}
    to prevent create_all() from running on the wrong database.
"""

import os
from flask import Flask, render_template
from app.models import db
from dotenv import load_dotenv
from urllib.parse import quote
from datetime import datetime

# Import Blueprints for modular route organization
from app.routes.dashboard import dashboard_bp
from app.routes.intervenants import intervenants_bp
from app.routes.clients import clients_bp
from app.routes.projets import projets_bp
from app.routes.interactions import interactions_bp
from app.routes.api import api_bp

load_dotenv()

def create_app():
        """
        Application factory function for TNS.

        - Loads configuration from environment variables.
        - Initializes the database.
        - Registers error handlers and blueprints.
        - Injects the current year into all templates.
        """

        # Load database credentials from environment variables
        DB_USER = os.getenv("DB_USER")
        db_password = os.getenv("DB_PASSWORD")
        DB_PASSWORD = quote(db_password.encode()) if db_password is not None else ""
        DB_HOST = os.getenv("DB_HOST")
        DB_PORT = os.getenv("DB_PORT")
        DB_NAME = os.getenv("DB_NAME")
        DATABASE_URI = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

        app = Flask(__name__)

        # Configure the Flask app
        app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

        # Initialize the database with the app
        db.init_app(app)

        # Custom error handler for 404 errors
        @app.errorhandler(404)
        def page_not_found(e):
                """Render a custom 404 error page."""
                return render_template('404.html'), 404

        # Inject the current year into all templates
        def inject_current_year():
                """Make the current year available in all templates."""
                return {"current_year": datetime.now().year}

        app.context_processor(inject_current_year)

        # Register all blueprints for modular route handling
        app.register_blueprint(dashboard_bp)
        app.register_blueprint(intervenants_bp)
        app.register_blueprint(clients_bp)
        app.register_blueprint(projets_bp)
        app.register_blueprint(interactions_bp)
        app.register_blueprint(api_bp)

        return app
