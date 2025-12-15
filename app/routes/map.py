from flask import Blueprint, jsonify, render_template, request
from app.models import Client, db
import requests

map_bp = Blueprint("map", __name__, url_prefix="/map")

@map_bp.route("/")
def map_page():
    return render_template("map.html")

@map_bp.route("/api")
def clients_api():
    clients = Client.query.all()

    return jsonify([ # c'est pour la carte qui est faite en JS : elle a besoin de JSON
        {
            "id": c.id_client,
            "name": c.raison_sociale,
            "secteur": c.secteur,
            "lat": c.latitude,
            "lng": c.longitude
        }
        for c in clients
    ])

@map_bp.route("/<int:radius>")
def prospects_api(radius):

    CENTER_LAT = 48.66895
    CENTER_LNG = 6.15547

    query = f"""
    [out:json];
    (
      node["shop"](around:{radius},{CENTER_LAT},{CENTER_LNG});
      node["office"](around:{radius},{CENTER_LAT},{CENTER_LNG});
      node["craft"](around:{radius},{CENTER_LAT},{CENTER_LNG});
    );
    out;
    """

    response = requests.post(
        "https://overpass-api.de/api/interpreter",
        data=query
    )

    data = response.json()

    prospects = []
    for el in data["elements"]:
        tags = el.get("tags", {})

        prospects.append({
            "name": tags.get("name", "Entreprise inconnue"),
            "type": (
                tags.get("shop")
                or tags.get("office")
                or tags.get("craft")
                or "inconnu"
            ),
            "lat": el["lat"],
            "lng": el["lon"]
        })
    
    return jsonify(prospects)

@map_bp.route("/add_prospect", methods=["POST"])
def add_prospect():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "Aucune donnée reçue"}), 400

    lat = data.get("lat")
    lng = data.get("lng")
    name = data.get("name")
    type_ = data.get("type")

    if not all([lat, lng, name, type_]):
        return jsonify({"success": False, "message": "Données manquantes"}), 400
    
    existing = Client.query.filter_by(
        raison_sociale=name,
        latitude=lat,
        longitude=lng
    ).first()

    if existing:
        return jsonify({"success": False, "message": "Client déjà présent dans la base"}), 200

    prospect = Client(
        id_client=None,
        raison_sociale=name,
        mail_client=None,
        telephone_client=None,
        date_dernier_contact=None,
        secteur=type_,
        latitude=lat,
        longitude=lng
    )
    db.session.add(prospect)
    db.session.commit()

    return jsonify({"success": True, "id": prospect.id_client})

@map_bp.route("/delete_client/<int:client_id>", methods=["DELETE"])
def delete_client(client_id):
    client = Client.query.get(client_id)
    if not client:
        return jsonify({"success": False, "message": "Client introuvable"}), 404

    db.session.delete(client)
    db.session.commit()

    return jsonify({"success": True})



