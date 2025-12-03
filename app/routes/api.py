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

@api_bp.get("/clients/<int:id_client>")
def get_client(id_client: int):
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

@api_bp.route("/clients/add", methods=["POST"])
def add_client():
    client_data = request.get_json()
    client = Client(
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

@api_bp.route("/clients/<int:id_client>", methods=["PUT"])
def update_client(id_client):
    client_data = request.get_json()
    client = Client.query.get_or_404(id_client) # si le client n'est pas trouvé -> 404

    client.raison_sociale = client_data.get("raison_sociale", client.raison_sociale)
    client.mail_client = client_data.get("mail_client", client.mail_client)
    client.telephone_client = client_data.get("telephone_client", client.telephone_client)
    client.secteur = client_data.get("secteur", client.secteur)
    client.dernier_contact = client_data.get("dernier_contact", client.dernier_contact)
    client.latitude = client_data.get("latitude", client.latitude)
    client.longitude = client_data.get("longitude", client.longitude)

    db.session.commit()
    return jsonify({"message": "Client updated", "client": client_data})

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
