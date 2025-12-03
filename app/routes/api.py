from flask import Blueprint, jsonify, request
from app.models import db, Client
from sqlalchemy.exc import ProgrammingError



api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/clients/get_all")
def get_all_clients():
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
def get_client():
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
def update_client():
    client_data = request.get_json()
    id_client = request.args.get('id')
    confirm_change_id = request.args.get('confirm_change_id')
    client: Client = Client.query.get_or_404(id_client) # si le client n'est pas trouvé -> 404

    # On vérifie que le client modifié à bien le même ID pour éviter de futur erreurs
    if id_client != client_data.get('id_client') and confirm_change_id == None:
            return jsonify({
                'message': 'client IDs not matching, confirmation needed !',
                'current_ID': client.id_client,
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

# TODO : Rework la route pour qu'elle soit sous le format /api/clients (comme les autres) => Récupérer l'id dans la requête
@api_bp.route("/clients/<int:id_client>", methods=["DELETE"])
def delete_client(id_client):
    client = Client.query.get_or_404(id_client)
    try:
        db.session.delete(client)
        db.session.commit()
    except ProgrammingError as e:
        db.session.rollback()  # important pour ne pas bloquer la session
        return jsonify({"Erreur":"", "details": str(e)}), 500

    return jsonify({"message": f"Client {id_client} deleted"})
