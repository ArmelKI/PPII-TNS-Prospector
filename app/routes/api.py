from flask import Blueprint, jsonify, request
from app.models import *
from sqlalchemy.exc import ProgrammingError
from app.permissions import manage_clients_required, manage_users_required

api_bp = Blueprint("api", __name__, url_prefix="/api")

@api_bp.route("/clients/get_all")
@manage_clients_required
def get_all_clients():
    """
    Retourne un JSON des données sur tous les clients
    """
    clients: list[Client] = Client.query.all()
    output = [{
        'id_client': client.id_client,
        'raison_sociale': client.raison_sociale,
        'mail_client': client.mail_client,
        'telephone_client': client.telephone_client,
        'secteur': client.secteur,
        'date_dernier_contact': client.date_dernier_contact,
        'latitude': client.latitude,
        'longitude': client.longitude,
    } for client in clients]
    return jsonify(output)

@api_bp.get("/clients")
@manage_clients_required
def get_client():
    """
    Retourne un JSON contenant les infos sur un client spécifique
    """
    id_client = request.args.get('id')
    client: Client = Client.query.get_or_404(id_client)
    output = {
        'id_client': client.id_client,
        'raison_sociale': client.raison_sociale,
        'mail_client': client.mail_client,
        'telephone_client': client.telephone_client,
        'secteur': client.secteur,
        'date_dernier_contact': client.date_dernier_contact,
        'latitude': client.latitude,
        'longitude': client.longitude,
    }
    return jsonify(output)

@api_bp.post("/clients")
@manage_clients_required
def add_client():
    client_data = request.get_json()
    client: Client = Client(
        id_client=client_data["id_client"],
        raison_sociale=client_data["raison_sociale"],
        mail_client=client_data["mail_client"],
        telephone_client=client_data["telephone_client"],
        secteur=client_data["secteur"],
        date_dernier_contact=client_data["date_dernier_contact"],
        latitude=client_data["latitude"],
        longitude=client_data["longitude"]
    )
    db.session.add(client)
    db.session.commit()
    return jsonify(client_data)

@api_bp.put("/clients")
@manage_clients_required
def update_client():
    client_data = request.get_json()
    id_client = request.args.get('id', type=int)
    confirm_change_id = request.args.get('confirm_change_id')
    client: Client = Client.query.get_or_404(id_client) # si le client n'est pas trouvé -> 404

    # On vérifie que le client modifié à bien le même ID pour éviter de futur erreurs
    if id_client != client_data.get('id_client') and confirm_change_id == None:
            return jsonify({
                'message': 'client IDs not matching, confirmation needed !',
                'current_ID': id_client,
                'new_id': client_data.get('id_client'),
            })

    client.id_client = client_data.get("id_client", client.id_client)
    client.raison_sociale = client_data.get("raison_sociale", client.raison_sociale)
    client.mail_client = client_data.get("mail_client", client.mail_client)
    client.telephone_client = client_data.get("telephone_client", client.telephone_client)
    client.secteur = client_data.get("secteur", client.secteur)
    client.date_dernier_contact = client_data.get("date_dernier_contact", client.date_dernier_contact)
    client.latitude = client_data.get("latitude", client.latitude)
    client.longitude = client_data.get("longitude", client.longitude)

    db.session.flush()
    db.session.commit()
    return jsonify({"message": "Client updated", "client": client_data})

@api_bp.delete("/clients")
@manage_clients_required
def delete_client():
    id_client = request.args.get('id')
    client = Client.query.get_or_404(id_client)
    db.session.delete(client)
    db.session.commit()
    return jsonify({"message": f"Client {id_client} deleted"})

@api_bp.route("/users/get_all")
def get_all_users():
    users: list[Utilisateur] = Utilisateur.query.all()
    output = [{
        'id_utilisateur': user.id_utilisateur,
        'prenom_utilisateur': user.prenom_utilisateur,
        'nom_utilisateur': user.nom_utilisateur,
        'mail_utilisateur': user.mail_utilisateur,
        'mdp_utilisateur': user.mdp_utilisateur,
        'id_role': user.id_role,
    } for user in users]
    return jsonify(output)

@api_bp.get("/users")
@manage_users_required
def get_user():
    id_utilisateur = request.args.get('id')
    user: Utilisateur = Utilisateur.query.get_or_404(id_utilisateur)
    output = {
        'id_utilisateur': user.id_utilisateur,
        'prenom_utilisateur': user.prenom_utilisateur,
        'nom_utilisateur': user.nom_utilisateur,
        'mail_utilisateur': user.mail_utilisateur,
        'mdp_utilisateur': user.mdp_utilisateur,
        'id_role': user.id_role,
    }
    return jsonify(output)

@api_bp.post("/users")
@manage_users_required
def add_user():
    user_data = request.get_json()
    user = Utilisateur(
        id_utilisateur = user_data["id_utilisateur"],
        prenom_utilisateur = user_data["prenom_utilisateur"],
        nom_utilisateur = user_data["nom_utilisateur"],
        mail_utilisateur = user_data["mail_utilisateur"],
        mdp_utilisateur = user_data["mdp_utilisateur"],
        id_role = user_data["id_role"]
    )
    db.session.add(user)
    db.session.commit()
    return jsonify(user_data)

@api_bp.put("/users")
@manage_users_required
def update_user():
    user_data = request.get_json()
    id_utilisateur = request.args.get('id')
    confirm_change_id = request.args.get('confirm_change_id')
    user: Utilisateur = Utilisateur.query.get_or_404(id_utilisateur) # si le client n'est pas trouvé -> 404

    # On vérifie que le client modifié à bien le même ID pour éviter de futur erreurs
    if id_utilisateur != user_data.get('id_utilisateur') and confirm_change_id == None:
            return jsonify({
                'message': 'users IDs not matching, confirmation needed !',
                'current_ID': id_utilisateur,
                'new_id': user_data.get('id_utilisateur'),
            })

    user.prenom_utilisateur = user_data.get("prenom_utilisateur", user.prenom_utilisateur)
    user.nom_utilisateur = user_data.get("nom_utilisateur", user.nom_utilisateur)
    user.mail_utilisateur = user_data.get("mail_utilisateur", user.mail_utilisateur)
    user.mdp_utilisateur = user_data.get("mdp_utilisateur", user.mdp_utilisateur)
    user.id_role = user_data.get("id_role", user.id_role)

    db.session.flush()
    db.session.commit()
    return jsonify({"message": "User updated", "user": user_data})

@api_bp.delete("/users")
@manage_users_required
def delete_user(id_client):
    id_utilisateur = request.args.get('id')
    user: Utilisateur = Utilisateur.query.get_or_404(id_utilisateur)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": f"User {id_client} deleted"})
