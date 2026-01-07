from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import Client, Convention, Projet, InteractionClient, db, EtatRelation
from datetime import date
from flask_login import login_required
from app.permissions import manage_clients_required

clients_bp = Blueprint("clients", __name__, url_prefix="/clients")

@clients_bp.route("/")
@login_required
def liste_clients():
    """
    Displays the list of all clients ordered alphabetically.
    """
    search_query = request.args.get('search', '').strip()
    page = request.args.get('page', 1, type=int)
    q = Client.query
    if search_query:
        q = q.filter(
            Client.raison_sociale.ilike(f"%{search_query}%") |
            Client.secteur.ilike(f"%{search_query}%")
        )
    clients_pagination = q.order_by(Client.raison_sociale).paginate(page=page, per_page=10)
    return render_template("clients.html", clients=clients_pagination, search_query=search_query)

@clients_bp.route("/add", methods=["GET", "POST"])
@manage_clients_required
def ajouter_client():
    """
    Handles the creation of a new client.
    """
    if request.method == "POST":
        nom = request.form.get("raison_sociale")
        mail = request.form.get("mail_client")
        tel = request.form.get("telephone_client")
        secteur = request.form.get("secteur")

        # Basic validation
        if not nom:
            flash("The client name is mandatory!", "danger")
            return render_template("ajouter_client.html")

        # Check for duplicates
        if Client.query.filter_by(raison_sociale=nom).first():
            flash("This client already exists!", "warning")
            return render_template("ajouter_client.html")

        # Create the client object
        # Note: We initialize latitude/longitude to 0.0 as they are required by the model
        new_client = Client(
            id_client=None, # Let the DB handle the ID
            raison_sociale=nom,
            mail_client=mail,
            telephone_client=tel,
            secteur=secteur,
            date_dernier_contact=date.today(),
            latitude=0.0,
            longitude=0.0
        )
        db.session.add(new_client)
        db.session.commit()

        flash(f"Client '{nom}' added successfully!", "success")
        return redirect(url_for('clients.details_client', id=new_client.id_client))

    return render_template("ajouter_client.html")

@clients_bp.route("/<int:id>")
@login_required
def details_client(id):
    """
    Shows the detailed profile of a client.
    """
    client: Client = Client.query.get_or_404(id)
    interactions = InteractionClient.query.order_by(InteractionClient.date_interaction.desc()).where(InteractionClient.id_client == client.id_client).all()
    # We fetch relationship states to populate the dropdown in the interaction form
    etats = EtatRelation.query.all()

    return render_template("details_clients.html", client=client, etats=etats, interactions=interactions)

@clients_bp.route("/edit/<int:id>", methods=["GET", "POST"])
@manage_clients_required
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
@manage_clients_required
def supprimer_client(id):
    """
    Deletes a client and all associated data (Projects, Interactions, Conventions).
    This is a destructive action, handle with care.
    """
    client = Client.query.get_or_404(id)

    try:
        # 1. Delete all interactions linked to this client
        InteractionClient.query.filter_by(id_client=id).delete()

        # 2. Handle Conventions and Projects manually to be safe
        # (Explicit deletion prevents orphan errors if cascades aren't perfect)
        for convention in client.conventions:
            for projet in convention.projets:
                db.session.delete(projet)
            db.session.delete(convention)

        # 3. Finally, delete the client
        db.session.delete(client)
        db.session.commit()

        flash("Client and all related records deleted successfully.", "success")
        return redirect(url_for("clients.liste_clients"))

    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting client", "danger")
        raise e
        return redirect(url_for("clients.details_client", id=id))
