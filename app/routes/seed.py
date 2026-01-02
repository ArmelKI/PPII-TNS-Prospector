from flask import Blueprint, request, jsonify
from app import db
from app.models import (
    Role, Utilisateur, Client, EtatRelation, InteractionClient, 
    Competence, Intervenant, Projet, Jalon, Tache, Convention, # Fixed Jalon import
    StatutProjet, StatutJalon, StatutTache
)
from datetime import datetime

seed_bp = Blueprint('seed', __name__, url_prefix='/api/seed')

@seed_bp.route('/<model_name>', methods=['POST'])
def seed_data(model_name):
    data = request.get_json()
    if not isinstance(data, list):
        return jsonify({"error": "Payload must be a list of objects"}), 400

    try:
        objects_to_add = []
        
        def parse_date(date_str):
            return datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else None

        for item in data:
            if model_name == 'roles':
                obj = Role(**item)
            
            elif model_name == 'etats_relation':
                obj = EtatRelation(**item)

            elif model_name == 'competences':
                obj = Competence(**item)

            elif model_name == 'clients':
                # Map date fields
                if 'date_dernier_contact' in item:
                    item['date_dernier_contact'] = parse_date(item['date_dernier_contact'])
                
                # IMPORTANT: If you kept the __init__ in Client model, 
                # you must provide id_client in JSON or remove __init__ from models.py
                obj = Client(**item)

            elif model_name == 'conventions':
                item['date_debut_convention'] = parse_date(item.get('date_debut_convention'))
                item['date_fin_convention'] = parse_date(item.get('date_fin_convention'))
                obj = Convention(**item)

            elif model_name == 'users':
                obj = Utilisateur(**item)

            elif model_name == 'intervenants':
                obj = Intervenant(**item)

            elif model_name == 'projets':
                item['date_debut_projet'] = parse_date(item.get('date_debut_projet'))
                item['date_fin_projet'] = parse_date(item.get('date_fin_projet'))
                # Handle Enum String to Object conversion manually if needed
                # (SQLAlchemy often handles this automatically if string matches enum value, but let's be safe)
                if 'statut_projet' in item:
                    # Find the Enum member where value equals the string
                    for e in StatutProjet:
                        if e.value == item['statut_projet']:
                            item['statut_projet'] = e
                            break
                obj = Projet(**item)

            elif model_name == 'jalons':
                item['date_debut_jalon'] = parse_date(item.get('date_debut_jalon'))
                item['date_fin_jalon'] = parse_date(item.get('date_fin_jalon'))
                
                if 'statut_jalon' in item:
                    for e in StatutJalon:
                        if e.value == item['statut_jalon']:
                            item['statut_jalon'] = e
                            break
                obj = Jalon(**item) # Fixed class name

            elif model_name == 'taches':
                item['date_dernier_delai_tache'] = parse_date(item.get('date_dernier_delai_tache'))
                
                if 'statut_tache' in item:
                    for e in StatutTache:
                        if e.value == item['statut_tache']:
                            item['statut_tache'] = e
                            break
                obj = Tache(**item)

            else:
                return jsonify({"error": f"Model '{model_name}' not recognized"}), 404

            objects_to_add.append(obj)

        db.session.add_all(objects_to_add)
        db.session.commit()
        return jsonify({"message": f"{len(objects_to_add)} rows inserted into {model_name}"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500