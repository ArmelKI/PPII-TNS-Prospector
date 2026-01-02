from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import Projet, Client, Convention, StatutProjet, Intervenant, db
from datetime import date, datetime
from app.matching import call_ai_matching, create_ai_prompt
import json
from flask_login import login_required


projets_bp = Blueprint("projets", __name__, url_prefix="/projets")

@projets_bp.route("/")
@login_required
def liste_projets():
    """
    Displays the main list of projects.
    Fetches all projects from the database to be displayed in cards.
    """
    tous_les_projets = Projet.query.all()
    return render_template("projets.html", projets=tous_les_projets)

@projets_bp.route("/add", methods=["GET", "POST"])
@login_required
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
            clients = Client.query.order_by(Client.raison_sociale).all() # type: ignore
            return render_template("ajouter_projet.html",
                                 clients=clients,
                                 selected_client=id_client), 200

        conv = Convention(
            id_client=id_client,   # type: ignore
            type_convention=type_convention, # type: ignore
            date_debut_convention=date.today(), # type: ignore
            prix=prix # type: ignore
        )
        db.session.add(conv)
        db.session.flush()

        proj = Projet(
            nom_projet=nom_projet, # type: ignore
            statut_projet=StatutProjet.PAS_COMMENCE, # type: ignore
            date_debut_projet=date.today(), # type: ignore
            id_convention=conv.id_convention # type: ignore
        )
        db.session.add(proj)
        db.session.commit()

        flash("Projet ajouté avec succès.", "success")
        return redirect(url_for('jalons.voir_kanban', id_projet=proj.id_projet))

    clients = Client.query.order_by(Client.raison_sociale).all() # type: ignore
    selected_client = request.args.get('client', type=int)
    return render_template("ajouter_projet.html", clients=clients, selected_client=selected_client)

@projets_bp.route("/details/<int:id>")
@login_required
def details_projet(id):
    """
    Shows the details of a specific project (Team, Budget, Status).
    """
    projet = Projet.query.get_or_404(id)
    return render_template("details_projet.html", projet=projet)

@projets_bp.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def modifier_projet(id):
    """
    Route to edit an existing project.
    Allows updating status, dates, and assigned team members.
    """
    projet = Projet.query.get_or_404(id)

    if request.method == "POST":
        projet.nom_projet = request.form.get("nom_projet")
        date_debut = request.form.get("date_debut")
        date_fin = request.form.get("date_fin")

        if date_debut:
            projet.date_debut_projet = datetime.strptime(date_debut, '%Y-%m-%d').date()
        if date_fin:
            projet.date_fin_projet = datetime.strptime(date_fin, '%Y-%m-%d').date()


        new_statut = request.form.get("statut_projet")
        for s in StatutProjet:
            if s.value == new_statut:
                projet.statut_projet = s
                break

        intervenant_ids = request.form.getlist("intervenants")
        projet.intervenants = [] # Reset
        for i_id in intervenant_ids:
            intervenant = Intervenant.query.get(int(i_id))
            if intervenant:
                projet.intervenants.append(intervenant)

        db.session.commit()
        flash("Projet mis à jour avec succés.", "success")
        return redirect(url_for("projets.details_projet", id=projet.id_projet))

    tous_intervenants = Intervenant.query.all()

    return render_template(
        "modifier_projet.html",
        projet=projet,
        intervenants=tous_intervenants,
        StatutProjet=StatutProjet
    )


@projets_bp.route("/delete/<int:id>", methods=["POST"])
def supprimer_projet(id):
    """
    Deletes a specific project.
    Redirects back to the client's page if possible, otherwise to the project list.
    """
    projet = Projet.query.get_or_404(id)
    client_id = projet.convention.id_client if projet.convention else None
    
    try:
        db.session.delete(projet)
        db.session.commit()
        flash("Projet supprimé.", "info")
        
        if client_id:
            return redirect(url_for("clients.details_client", id=client_id))
        return redirect(url_for("projets.liste_projets"))
        
    except Exception as e:
        db.session.rollback()
        flash("Could not delete project.", "danger")
        return redirect(url_for("projets.details_projet", id=id))

@projets_bp.route("/<int:id>/match",methods=['GET'])
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