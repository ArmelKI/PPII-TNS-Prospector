
from flask import render_template, Blueprint, jsonify, request , session # Blueprint pour les routes
from app.models import Projet , db


projets_bp = Blueprint('projets',__name__,url_prefix="/projets")




@projets_bp.route('/')
def liste_projets():
    
    projets = Projet.query.all()  # SELECT * FROM projets
    return render_template('projets.html', projets = projets)




# Les suppressions de projets ne pose pas de probleme pour  le moment mais il faudra faire attention au effet de cascade 
# On ne peut pas supprimer un client qui est déja relié à un projet (par sécurité)

@projets_bp.route('/', methods=['POST'])
def  supprimer_projet(id): 
    pass


@projets_bp.route('/<int:id>' ,methods=['GET']) # Détail d'un projet
def detail_projet(id):
    projet = Projet.query.get_or_404(id)
    return render_template('detail_projet.html',projet = projet)
    


@projets_bp.route('/add' ,methods=['GET'])
def ajouter_projet_form():
    return render_template('ajouter_projet.html')


@projets_bp.route('/add' ,methods=['POST'])
def ajouter_projet_data():
    projetData = request.get_json()
    nouveau_projet = Projet (
        nom_projet =  projetData["nom_projet"],
        statut_projet = projetData["statut_projet"],
        date_debut_projet = projetData["date_debut_projet"],
        date_fin_projet = projetData["date_fin_projet"],
        id_convention = projetData["id_convention"]
        ) 
    # On récupére les infos du nouveau projet dans la requete


    # 3. On sauvegarde dans la DB 
    try:
        db.session.add(nouveau_projet)
        db.session.commit()
        return jsonify({"message": "Succès ! Projet créé", "id": nouveau_projet.id_projet}), 201
    except Exception as e:
        return jsonify({"erreur": str(e)}), 400
    

# on pourra editer un projet via un bouton sur détail projet et peut etre aussi
@projets_bp.route('/edit/<int:id>', methods=['GET'])
def modifier_projet():
    pass