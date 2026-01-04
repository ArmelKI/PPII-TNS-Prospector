import os
from flask import Flask, render_template
from app.models import db, Utilisateur
from dotenv import load_dotenv
from urllib.parse import quote
from datetime import datetime
from app.config import login_manager
from app.permissions import all_perms

# Import Blueprints
from app.routes.dashboard import dashboard_bp
from app.routes.intervenants import intervenants_bp
from app.routes.clients import clients_bp
from app.routes.projets import projets_bp
from app.routes.interactions import interactions_bp
from app.routes.jalons import jalons_bp
from app.routes.api import api_bp
from app.routes.map import map_bp
from app.routes.auth import auth_bp

load_dotenv()


def create_app():
    """
    Application factory for TNS.
    - Loads config from environment variables.
    - Initializes DB.
    - Registers blueprints.
    """

    # 1. Database Configuration
    DB_USER = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD", "")
    DB_PASSWORD = quote(db_password.encode()) if db_password else ""
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "tns_db")

    # Construct the PostgreSQL connection string
    DATABASE_URI = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev_key_fallback')

    # Optional: Set max upload size (e.g., 16MB)
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

    # 2. Initialize Extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login_page'
    login_manager.login_message = 'Veuillez vous connectez pour accéder à cette page.'

    # 3. Global Template Helpers
    @app.errorhandler(404)
    def page_not_found(e):
        """Render a custom 404 error page."""
        return render_template('404.html'), 404

    @app.context_processor
    def inject_global_vars():
        """Make current_year available in all templates."""
        return {"current_year": datetime.now().year}

    # 4. Check for special accounts in db
    special_accounts = {
        'admin': {
            'prenom_utilisateur': 'admin',
            'nom_utilisateur': 'admin',
            'mail_utilisateur': 'admin',
            'mdp_utilisateur': '$2b$12$tgFWQzanVpp8MO9CGlV45ulmkjtPD2iSMmWN5RFRxzOAB1UAdvXeq',
            'permission': all_perms
        }
    }
    app.config['special_accounts_mails'] = [account['mail_utilisateur'] for account in special_accounts.values()]

    with app.app_context():
        for account in special_accounts.values():
            user: Utilisateur = Utilisateur.query.where(Utilisateur.mail_utilisateur == account['mail_utilisateur']).scalar()
            if user is None:
                new_user = Utilisateur(
                    prenom_utilisateur=account['prenom_utilisateur'],
                    nom_utilisateur=account['nom_utilisateur'],
                    mail_utilisateur=account['mail_utilisateur'],
                    mdp_utilisateur=account['mdp_utilisateur'],
                    permission=account['permission'],
                    id_role=1
                )
                db.session.add(new_user)
                db.session.commit()

    # 5. Register Blueprints
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(intervenants_bp)
    app.register_blueprint(clients_bp)
    app.register_blueprint(projets_bp)
    app.register_blueprint(interactions_bp)
    app.register_blueprint(jalons_bp) # Kanban logic
    app.register_blueprint(api_bp)
    app.register_blueprint(map_bp)
    app.register_blueprint(auth_bp)

    return app
