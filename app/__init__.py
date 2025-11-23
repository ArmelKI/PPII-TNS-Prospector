"""
app.__init__ — Factory pour l'application TNS (version test-friendly)

- Accepts optional `test_config` dict that will override app.config before DB init.
- Uses `AUTO_CREATE_DB` config key to control whether to call db.create_all().
  Tests should pass {"AUTO_CREATE_DB": False, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"}
  so that create_all() is not executed on the wrong DB.
"""

import os
from urllib.parse import quote
from flask import Flask, render_template
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

from app.models import db

def create_app(test_config: dict | None = None):
    """Create and configure the Flask app.
    If test_config is provided, it overrides default config before DB init.
    """
    app = Flask(__name__, template_folder="templates", static_folder="static")

    # Default config
    DB_USER = os.getenv("DB_USER", "")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_NAME = os.getenv("DB_NAME", "")

    if DB_USER and DB_PASSWORD and DB_NAME:
        db_pass = quote(DB_PASSWORD)
        app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{DB_USER}:{db_pass}@{DB_HOST}/{DB_NAME}?sslmode=require'
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "sqlite:///tns_dev.db")

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "dev-secret-key")

    # Allow tests to override config BEFORE we init db
    if test_config:
        app.config.update(test_config)

    # init extensions
    db.init_app(app)

    # Register blueprints lazily (avoid circular imports)
    from app.routes.dashboard import dashboard_bp
    from app.routes.intervenants import intervenants_bp
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(intervenants_bp)

    # Only create DB tables automatically if the config allows it
    # Default True for convenience in local dev; tests will set AUTO_CREATE_DB=False
    if app.config.get("AUTO_CREATE_DB", True):
        with app.app_context():
            db.create_all()

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("404.html"), 404
    
    from app.routes.media import media_bp
    app.register_blueprint(media_bp)

    from .routes.clients import clients
    app.register_blueprint(clients)

    from .routes.projets import projets
    app.register_blueprint(projets)

    from .routes.interactions import interactions
    app.register_blueprint(interactions)

    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB

    app.context_processor(inject_current_year)

    return app


def inject_current_year():
    return {"current_year": datetime.now().year}
