from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import Projet
from datetime import date
from app.models import Client, Convention, Projet, StatutProjet, db

projets_bp = Blueprint("projets", __name__, url_prefix="/projets")

@projets_bp.route("/")
def liste_projets():
    # Load projects with related clients (via convention) to avoid display errors
    tous_les_projets = Projet.query.all()
    return render_template("projets.html", projets=tous_les_projets)

@projets_bp.route("/details/<int:id>")
def details_projet(id):
    # On charge le projet avec ses intervenants et le client
    projet = Projet.query.get_or_404(id)
    return render_template("details_projet.html", projet=projet)

@projets_bp.route("/add", methods=["GET", "POST"])
def ajouter_projet():
    if request.method == "POST":
        id_client = request.form.get("id_client")
        nom_projet = request.form.get("nom_projet")
        prix = request.form.get("prix", type=float)
        
        # 1. Création auto de la convention (simplifié pour le projet)
        conv = Convention(
            id_client=id_client, # type: ignore
            type_convention = request.form.get("type_convention"), # type: ignore
            date_debut_convention=date.today(), # type: ignore
            prix=prix # type: ignore
        )
        db.session.add(conv)
        db.session.flush() # Pour avoir l'ID
        
        # 2. Création du projet
        proj = Projet(
            nom_projet=nom_projet, # type: ignore
            statut_projet=StatutProjet.PAS_COMMENCE, # type: ignore
            date_debut_projet=date.today(), # type: ignore
            id_convention=conv.id_convention # type: ignore
        )
        db.session.add(proj)
        db.session.commit()
        
        flash("Projet créé !", "success")
        return redirect(url_for('jalons.voir_kanban', id_projet=proj.id_projet))

    # GET
    clients = Client.query.order_by(Client.raison_sociale).all() # type: ignore
    selected_client = request.args.get('client', type=int)
    return render_template("ajouter_projet.html", clients=clients, selected_client=selected_client)