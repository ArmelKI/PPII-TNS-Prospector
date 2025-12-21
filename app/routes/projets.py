from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import Projet, Client, Convention, StatutProjet, Intervenant, db
from datetime import date, datetime

projets_bp = Blueprint("projets", __name__, url_prefix="/projets")

@projets_bp.route("/")
def liste_projets():
    """
    Displays the main list of projects.
    Fetches all projects from the database to be displayed in cards.
    """
    tous_les_projets = Projet.query.all()
    return render_template("projets.html", projets=tous_les_projets)

@projets_bp.route("/add", methods=["GET", "POST"])
def ajouter_projet():
    """
    Handles the creation of a new project and its associated convention.
    """
    if request.method == "POST":
        id_client = request.form.get("id_client")
        nom_projet = request.form.get("nom_projet")
        prix = request.form.get("prix", type=float)
        type_convention = request.form.get("type_convention")

        if not id_client or not nom_projet or not type_convention:
            flash("Veuillez remplir tous les champs obligatoires.", "danger")
            # On recharge la liste des clients pour réafficher le formulaire proprement
            clients = Client.query.order_by(Client.raison_sociale).all()
            return render_template("ajouter_projet.html", 
                                 clients=clients, 
                                 selected_client=id_client), 200

        conv = Convention(
            id_client=id_client, # type: ignore
            type_convention=type_convention, # type: ignore
            date_debut_convention=date.today(), # type: ignore
            prix=prix # type: ignore
        )
        db.session.add(conv)
        db.session.flush()
        
        # 2. Create Project
        proj = Projet(
            nom_projet=nom_projet, # type: ignore
            statut_projet=StatutProjet.PAS_COMMENCE, # type: ignore
            date_debut_projet=date.today(), # type: ignore
            id_convention=conv.id_convention # type: ignore
        )
        db.session.add(proj)
        db.session.commit()
        
        flash("Project successfully created.", "success")
        return redirect(url_for('jalons.voir_kanban', id_projet=proj.id_projet))

    clients = Client.query.order_by(Client.raison_sociale).all() # type: ignore
    selected_client = request.args.get('client', type=int)
    return render_template("ajouter_projet.html", clients=clients, selected_client=selected_client)

@projets_bp.route("/details/<int:id>")
def details_projet(id):
    """
    Shows the details of a specific project (Team, Budget, Status).
    """
    projet = Projet.query.get_or_404(id)
    return render_template("details_projet.html", projet=projet)

@projets_bp.route("/edit/<int:id>", methods=["GET", "POST"])
def modifier_projet(id):
    """
    Route to edit an existing project.
    Allows updating status, dates, and assigned team members.
    """
    projet = Projet.query.get_or_404(id)

    if request.method == "POST":
        # Update scalar fields
        projet.nom_projet = request.form.get("nom_projet")
        
        # Date parsing
        date_debut = request.form.get("date_debut")
        date_fin = request.form.get("date_fin")
        
        if date_debut:
            projet.date_debut_projet = datetime.strptime(date_debut, '%Y-%m-%d').date()
        if date_fin:
            projet.date_fin_projet = datetime.strptime(date_fin, '%Y-%m-%d').date()
            
        # Update Status
        new_statut = request.form.get("statut_projet")
        for s in StatutProjet:
            if s.value == new_statut:
                projet.statut_projet = s
                break

        # Update Team (Many-to-Many)
        intervenant_ids = request.form.getlist("intervenants")
        projet.intervenants = [] # Reset
        for i_id in intervenant_ids:
            intervenant = Intervenant.query.get(int(i_id))
            if intervenant:
                projet.intervenants.append(intervenant)

        db.session.commit()
        flash("Project updated successfully.", "success")
        return redirect(url_for("projets.details_projet", id=projet.id_projet))

    # GET: Prepare form data
    tous_intervenants = Intervenant.query.all()
    
    return render_template(
        "modifier_projet.html", 
        projet=projet, 
        intervenants=tous_intervenants,
        StatutProjet=StatutProjet
    )