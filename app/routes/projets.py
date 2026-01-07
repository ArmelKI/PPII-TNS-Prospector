from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import Projet, Client, Convention, StatutProjet, Intervenant, db, Competence
from datetime import date, datetime
from app.matching import call_ai_matching, create_ai_prompt
import json
from flask_login import login_required
from app.permissions import manage_projets_required

projets_bp = Blueprint("projets", __name__, url_prefix="/projets")

@projets_bp.route("/")
@login_required
def liste_projets():
    """
    Displays the main list of projects.
    """
    search_query = request.args.get('search', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 9
    filter_statut = request.args.get('statut', '').strip()
    q = Projet.query.join(Convention, Projet.id_convention == Convention.id_convention)
    if search_query:
        q = q.filter(
            Projet.nom_projet.ilike(f"%{search_query}%") |
            Convention.client.has(Client.raison_sociale.ilike(f"%{search_query}%"))
        )
    if filter_statut:
        try:
            statut_enum = getattr(StatutProjet, filter_statut)
            q = q.filter(Projet.statut_projet == statut_enum)
        except AttributeError:
            pass
    projets_pagination = q.order_by(Projet.nom_projet).paginate(page=page, per_page=per_page, error_out=False)
    return render_template("projets.html", projets=projets_pagination, search_query=search_query, filter_statut=filter_statut)

@projets_bp.route("/add", methods=["GET", "POST"])
@manage_projets_required
def ajouter_projet():
    """
    Handles the creation of a new project, including workload and required skills.
    """
    if request.method == "POST":
        id_client = request.form.get("id_client")
        nom_projet = request.form.get("nom_projet")
        prix = request.form.get("prix", type=float)
        type_convention = request.form.get("type_convention")

        # 1. Retrieve the Workload (Charge)
        charge = request.form.get("charge_projet", type=int, default=0)

        if not id_client or not nom_projet:
            flash("Missing mandatory fields.", "danger")
            return redirect(request.url)

        # 2. Create Convention
        conv = Convention(
            id_client=id_client,
            type_convention=type_convention,
            date_debut_convention=date.today(),
            prix=prix
        )
        db.session.add(conv)
        db.session.flush()

        # 3. Create Project
        proj = Projet(
            nom_projet=nom_projet,
            statut_projet=StatutProjet.PAS_COMMENCE,
            date_debut_projet=date.today(),
            id_convention=conv.id_convention,
            charge_projet=charge  # <--- WE SAVE THE HOURS HERE
        )
        db.session.add(proj)

        # 4. Handle Required Skills (Many-to-Many)
        # We get the list of IDs checked in the form
        skill_ids = request.form.getlist("competences_requises")

        for sid in skill_ids:
            c = Competence.query.get(sid)
            if c:
                # SQLAlchemy handles the insert into 'projet_competence' table
                proj.competences_requises.append(c)

        db.session.commit()

        flash("Project created successfully.", "success")
        return redirect(url_for('projets.details_projet', id=proj.id_projet))

    clients = Client.query.order_by(Client.raison_sociale).all()
    # We pass all competences to the template for the checkbox list
    all_competences = Competence.query.order_by(Competence.nom_competence).all()
    selected_client = request.args.get('client', type=int)

    return render_template("ajouter_projet.html", clients=clients, competences=all_competences, selected_client=selected_client)
    # GET: Prepare data for the form
    clients = Client.query.order_by(Client.raison_sociale).all()
    all_competences = Competence.query.order_by(Competence.nom_competence).all()
    selected_client = request.args.get('client', type=int)

    return render_template("ajouter_projet.html",
                        clients=clients,
                        competences=all_competences,
                        selected_client=selected_client)

@projets_bp.route("/details/<int:id>")
@login_required
def details_projet(id):
    """
    Shows detailed overview: Team, Status, Budget, and Required Skills.
    """
    projet = Projet.query.get_or_404(id)
    return render_template("details_projet.html", projet=projet)

@projets_bp.route("/edit/<int:id>", methods=["GET", "POST"])
@manage_projets_required
def modifier_projet(id):
    """
    Route to edit an existing project.
    Allows updating status, dates, workload, required skills, and assigned team.
    """
    projet = Projet.query.get_or_404(id)

    if request.method == "POST":
        # 1. Update Basic Fields
        projet.nom_projet = request.form.get("nom_projet")
        # NEW: Update Workload
        projet.charge_projet = request.form.get("charge_projet", type=int, default=0)

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

        # 2. Update Required Skills (Many-to-Many)
        skill_ids = request.form.getlist("competences_requises")
        # We clear the current list and rebuild it based on the form
        projet.competences_requises = []
        for sid in skill_ids:
            c = Competence.query.get(sid)
            if c:
                projet.competences_requises.append(c)

        # 3. Update Team (Many-to-Many)
        intervenant_ids = request.form.getlist("intervenants")
        projet.intervenants = []
        for i_id in intervenant_ids:
            intervenant = Intervenant.query.get(int(i_id))
            if intervenant:
                projet.intervenants.append(intervenant)

        db.session.commit()
        flash("Project updated successfully.", "success")
        return redirect(url_for("projets.details_projet", id=projet.id_projet))

    # GET: Prepare data for the form
    tous_intervenants = Intervenant.query.all()
    # NEW: We need all skills to display the checklist
    toutes_competences = Competence.query.all()

    return render_template(
        "modifier_projet.html",
        projet=projet,
        intervenants=tous_intervenants,
        competences=toutes_competences, # Pass this to template
        StatutProjet=StatutProjet
    )

@projets_bp.route("/delete/<int:id>", methods=["POST"])
@manage_projets_required
def supprimer_projet(id):
    """
    Deletes a project.
    Redirects to client details if possible, otherwise project list.
    """
    projet = Projet.query.get_or_404(id)
    client_id = projet.convention.id_client if projet.convention else None

    try:
        db.session.delete(projet)
        db.session.commit()
        flash("Project deleted.", "info")

        if client_id:
            return redirect(url_for("clients.details_client", id=client_id))
        return redirect(url_for("projets.liste_projets"))

    except Exception as e:
        db.session.rollback()
        flash(f"Could not delete project: {e}", "danger")
        return redirect(url_for("projets.details_projet", id=id))

@projets_bp.route("/<int:id>/match",methods=['GET'])
@manage_projets_required
def match_projet(id):
    projet = Projet.query.get_or_404(id)
    intervenants  = Intervenant.query.filter_by (disponible = True).all()

    sys_p, usr_p = create_ai_prompt(projet, intervenants)
    suggestions = call_ai_matching(sys_p, usr_p)
    print(f"prompt system:{sys_p}")
    print(f"prompt user:{usr_p }")

    if suggestions:
        print("\n--- RÉSULTATS DU MATCHING ---")
        print(json.dumps(suggestions, indent=2, ensure_ascii=False))
    return  render_template('swipe.html', suggestions=suggestions['suggestions'],mission=projet)

@projets_bp.route("/<int:id>/valider-equipe",methods=['POST'])
@manage_projets_required
def valider_equipe(id):
    projet = Projet.query.get_or_404(id)

    equipe_json = request.form.get("equipe_data_json")

    try :
        if not equipe_json:
            raise ValueError("Aucune donnée d'équipe reçus.")
        membres_a_ajouter = json.loads(equipe_json)
        projet.intervenants = []

        for membre in membres_a_ajouter :
            id_inter = int(membre['id'])
            heures_a_prendre = int(membre['heures_attribuees'])

            intervenant = Intervenant.query.get(id_inter)

            if intervenant :
                projet.intervenants.append(intervenant)

                if intervenant.nb_heures_dispo >=  heures_a_prendre :
                    intervenant.nb_heures_dispo -= heures_a_prendre
                else:
                    intervenant.nb_heures_dispo = 0
                if  intervenant.nb_heures_dispo <= 0.5: # les heures dispos ne sont que des int
                    intervenant.disponible = False
        db.session.commit()
        flash("L'équipe à été validée et les disponibilités des intervenants mises à jours.", "success")
    except  json.JSONDecodeError :
        db.session.rollback()
        flash("Erreur de format des données (JSON invalide).", "danger")

    except  Exception as e:
        db.session.rollback()
        flash(f"Erreur lors de la sauvegarde : {str(e)}", "danger")

    return redirect(url_for('projets.details_projet',id=id))
