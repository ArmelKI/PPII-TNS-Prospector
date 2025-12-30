from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import Client, Convention, Projet, InteractionClient, db , EtatRelation
from datetime import date
from flask_login import login_required



clients_bp = Blueprint("clients", __name__, url_prefix="/clients")

@clients_bp.route("/")
@login_required
def liste_clients():
    tous_les_clients = Client.query.order_by(Client.raison_sociale).all() # type: ignore
    return render_template("clients.html", clients=tous_les_clients)

@clients_bp.route("/add", methods=["GET", "POST"])
@login_required
def ajouter_client():
    if request.method == "POST":
        nom = request.form.get("raison_sociale")
        mail = request.form.get("mail_client")
        tel = request.form.get("telephone_client")
        secteur = request.form.get("secteur")

        if not nom:
            flash("Le nom du client est obligatoire !", "danger")
            return render_template("ajouter_client.html")

        if Client.query.filter_by(raison_sociale=nom).first():
            flash("Ce client existe déjà !", "error")
            return render_template("ajouter_client.html")

        new_client = Client(
            id_client=None, # Laisse la BDD gérer l'ID
            raison_sociale=nom,
            mail_client=mail,
            telephone_client=tel,
            secteur=secteur,
            date_dernier_contact=date.today(),
            latitude=0, longitude=0
        )
        db.session.add(new_client)
        db.session.commit()

        flash(f"Client {nom} ajouté avec succès !", "success")
        return redirect(url_for('clients.details_client', id=new_client.id_client))

    return render_template("ajouter_client.html")

@clients_bp.route("/<int:id>")
@login_required
def details_client(id):
    client = Client.query.get_or_404(id)
    # ICI : On récupère la liste des états pour le menu déroulant (Select)
    etats = EtatRelation.query.all()

    return render_template("details_clients.html", client=client, etats=etats)

@clients_bp.route("/edit/<int:id>", methods=["GET", "POST"])
def modifier_client(id):
    """
    Route to edit an existing client's information.
    """
    client = Client.query.get_or_404(id)

    if request.method == "POST":
        # 1. Retrieve data from form
        client.raison_sociale = request.form.get("raison_sociale")
        client.secteur = request.form.get("secteur")
        client.mail_client = request.form.get("mail_client")
        client.telephone_client = request.form.get("telephone_client")
        # 2. Save changes
        db.session.commit()
        
        flash("Client information updated successfully.", "success")
        return redirect(url_for('clients.details_client', id=client.id_client))

    # GET: Render the form with current data
    return render_template("modifier_client.html", client=client)

@clients_bp.route("/delete/<int:id>", methods=["POST"])
def supprimer_client(id):
    """
    Deletes a client and all associated data (Projects, Interactions, Conventions).
    This is a destructive action.
    """
    client = Client.query.get_or_404(id)
    
    try:
        # 1. Delete all interactions linked to this client
        InteractionClient.query.filter_by(id_client=id).delete()
        
        # 2. Handle Conventions and Projects manually to be safe
        # (Though cascade delete in models is better, explicit deletion prevents orphan errors here)
        for convention in client.conventions:
            for projet in convention.projets:
                # Delete tasks and milestones if needed, or rely on DB cascade
                db.session.delete(projet)
            db.session.delete(convention)
            
        # 3. Finally, delete the client
        db.session.delete(client)
        db.session.commit()
        
        flash("Client and all related records deleted successfully.", "success")
        return redirect(url_for("clients.liste_clients"))
        
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting client: {str(e)}", "danger")
        return redirect(url_for("clients.details_client", id=id))