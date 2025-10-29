from flask import Flask, render_template
from app.routes.intervenants import intervenants_bp 
from app.models import db # Pour initialiser la BDD (quand elle sera prête)

def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")

    # Config temporaire pour SQLite (fichier local)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)  # Lie la BDD à l'app
   
    @app.route("/")
    def dashboard():
        # données de test (plus tard on récupèrera depuis la BDD)
        nb_clients = 5
        nb_projets = 3
        nb_intervenants = 8
        return render_template("dashboard.html",
                               nb_clients=nb_clients,
                               nb_projets=nb_projets,
                               nb_intervenants=nb_intervenants)
    app.register_blueprint(intervenants_bp)

    # Gestion d'erreur 404
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    return app