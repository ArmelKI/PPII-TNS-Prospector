from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import Projet, Client, Convention, StatutProjet, Intervenant, db
from datetime import date, datetime

projets_bp = Blueprint("projets", __name__, url_prefix="/projets")

@projets_bp.route("/")
def liste_projets():
    """
    Displays the main list of projects.
    
    We fetch all projects from the database. Thanks to SQLAlchemy's relationships,
    we can easily access the associated client (via the convention) directly in the template.
    """
    # Fetch all projects. SQLAlchemy will lazy-load the relationships (client/convention) when accessed.
    tous_les_projets = Projet.query.all()
    return render_template("projets.html", projets=tous_les_projets)

@projets_bp.route("/add", methods=["GET", "POST"])
def ajouter_projet():
    """
    Handles the creation of a new project.
    
    In this simplified workflow, creating a project also creates a 'Convention'
    behind the scenes, linking the project to a client.
    """
    if request.method == "POST":
        # 1. Grab data from the form
        id_client = request.form.get("id_client")
        nom_projet = request.form.get("nom_projet")
        prix = request.form.get("prix", type=float)
        type_convention = request.form.get("type_convention") # CC or CE

        # 2. Create the Convention first
        # A project must belong to a convention in our data model.
        conv = Convention(
            id_client=id_client, #  type: ignore
            type_convention=type_convention, # type: ignore
            date_debut_convention=date.today(), # type: ignore Start date is today
            prix=prix # type: ignore
        )
        db.session.add(conv)
        db.session.flush() # We flush here to generate the conv.id_convention immediately
        
        # 3. Create the Project
        proj = Projet(
            nom_projet=nom_projet, # type: ignore
            statut_projet=StatutProjet.PAS_COMMENCE, # type: ignore Default status
            date_debut_projet=date.today(), # type: ignore Start date is today
            id_convention=conv.id_convention # type: ignore Link it to the convention we just made
        )
        db.session.add(proj)
        db.session.commit()
        
        flash("Project successfully created! Let's get to work.", "success")
        # Redirect to the Kanban board so the user can start organizing tasks immediately
        return redirect(url_for('jalons.voir_kanban', id_projet=proj.id_projet))

    # GET request: We need the list of clients to populate the dropdown menu
    clients = Client.query.order_by(Client.raison_sociale).all() # type: ignore
    selected_client = request.args.get('client', type=int)
    
    return render_template("ajouter_projet.html", clients=clients, selected_client=selected_client)

@projets_bp.route("/details/<int:id>")
def details_projet(id):
    """
    Shows a detailed overview of a specific project.
    
    We use get_or_404 to automatically show a 'Page Not Found' error
    if the user tries to access a project ID that doesn't exist.
    """
    projet = Projet.query.get_or_404(id)
    return render_template("details_projet.html", projet=projet)

@projets_bp.route("/edit/<int:id>", methods=["GET", "POST"])
def modifier_projet(id):
    """
    Handles the modification of an existing project.
    
    This route allows updating the project's status, dates, and most importantly,
    the team members (Intervenants) assigned to it.
    """
    projet = Projet.query.get_or_404(id)

    if request.method == "POST":
        # --- 1. Basic Info Updates ---
        projet.nom_projet = request.form.get("nom_projet")
        
        # HTML date inputs return strings (YYYY-MM-DD), so we need to parse them
        # back into Python date objects.
        date_debut = request.form.get("date_debut")
        date_fin = request.form.get("date_fin")
        
        if date_debut:
            projet.date_debut_projet = datetime.strptime(date_debut, '%Y-%m-%d').date()
        if date_fin:
            projet.date_fin_projet = datetime.strptime(date_fin, '%Y-%m-%d').date()
            
        # --- 2. Status Update ---
        # The form sends a string (e.g., "En cours"). We need to find the matching Enum member.
        new_statut = request.form.get("statut_projet")
        for s in StatutProjet:
            if s.value == new_statut:
                projet.statut_projet = s
                break

        # --- 3. Team Management (The Tricky Part) ---
        # The form sends a list of IDs for the checked boxes (e.g., ['1', '4', '8'])
        intervenant_ids = request.form.getlist("intervenants")
        
        # We start by clearing the current team. This is the simplest way to handle
        # removals. We then rebuild the list from scratch based on the form.
        projet.intervenants = [] 
        
        for i_id in intervenant_ids:
            intervenant = Intervenant.query.get(int(i_id))
            if intervenant:
                # SQLAlchemy handles the association table insert automatically here
                projet.intervenants.append(intervenant)

        # Save everything to the database
        db.session.commit()
        flash("Project updated successfully.", "success")
        return redirect(url_for("projets.details_projet", id=projet.id_projet))

    # --- GET Request (Display Form) ---
    # We need ALL intervenants to display the full list of checkboxes.
    # The template will decide which ones to check based on the current project.
    tous_intervenants = Intervenant.query.all()
    
    return render_template(
        "modifier_projet.html", 
        projet=projet, 
        intervenants=tous_intervenants,
        StatutProjet=StatutProjet
    )