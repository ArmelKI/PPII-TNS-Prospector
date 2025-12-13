from flask import Blueprint, jsonify, render_template
from app.models import Client

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