from flask import Blueprint, request, jsonify, render_template
from app.models import db, Jalon, Projet, StatutJalon

jalons_bp = Blueprint("jalons", __name__, url_prefix="/jalons")

@jalons_bp.route("/kanban/<int:id_projet>")
def voir_kanban(id_projet):
    # On récupère le projet et ses jalons
    projet = Projet.query.get_or_404(id_projet)
    jalons = Jalon.query.filter_by(id_projet=id_projet).order_by(Jalon.date_fin_jalon).all()
    
    return render_template("projet_kanban.html", projet=projet, jalons=jalons)

@jalons_bp.route("/api/update_statut", methods=["POST"])
def update_statut():
    data = request.get_json()
    id_jalon = data.get("id_jalon")
    nouveau_statut_str = data.get("nouveau_statut") 

    jalon = Jalon.query.get_or_404(id_jalon)

    # On cherche directement la valeur dans l'Enum
    for s in StatutJalon:
        if s.value == nouveau_statut_str:
            jalon.statut_jalon = s
            db.session.commit()
            return jsonify({"success": True})
            
    return jsonify({"success": False, "error": "Statut inconnu"}), 400