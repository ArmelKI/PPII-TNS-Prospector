"""
Initialisation de l'application Flask
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app(config_object="config.Config"):
    app = Flask(__name__)
    app.config.from_object(config_object)

    db.init_app(app)

    # Import des blueprints
    from app.routes.dashboard import dashboard_bp
    from app.routes.intervenants import intervenants_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(intervenants_bp)

    return app

# Permet à Python de reconnaître ce dossier comme un package
# et d'éviter les erreurs d'importation circulaire.