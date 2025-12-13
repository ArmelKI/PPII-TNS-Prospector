from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import Client, EtatRelation, db
from datetime import date

clients_bp = Blueprint("clients", __name__, url_prefix="/clients")

@clients_bp.route("/")
def liste_clients():
    tous_les_clients = Client.query.order_by(Client.raison_sociale).all() # type: ignore
    return render_template("clients.html", clients=tous_les_clients)

@clients_bp.route("/add", methods=["GET", "POST"])
def ajouter_client():
    if request.method == "POST":
        # Récupération du formulaire
        nom = request.form.get("raison_sociale")
        mail = request.form.get("mail_client")
        tel = request.form.get("telephone_client")
        secteur = request.form.get("secteur")
        
        # Création
        new_client = Client(
            id_client=None, # Laisse la BDD gérer l'ID
            raison_sociale=nom,
            mail_client=mail,
            telephone_client=tel,
            secteur=secteur,
            date_dernier_contact=date.today(),
            latitude=0, longitude=0 # On gérera la géoloc plus tard (API Bonus)
        )
        db.session.add(new_client)
        db.session.commit()
        
        flash(f"Client {nom} ajouté avec succès !", "success")
        return redirect(url_for('clients.details_client', id=new_client.id_client))
        
    return render_template("ajouter_client.html")

@clients_bp.route("/<int:id>")
def details_client(id):
    client = Client.query.get_or_404(id)
    # ICI : On récupère la liste des états pour le menu déroulant (Select)
    etats = EtatRelation.query.all()
    
    return render_template("details_clients.html", client=client, etats=etats)