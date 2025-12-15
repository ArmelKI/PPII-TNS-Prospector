
from flask import render_template, Blueprint, jsonify, request , session, redirect, url_for , flash # Blueprint pour les routes
from app.models import Projet , db


projets_bp = Blueprint('projets',__name__,url_prefix="/projets")




@projets_bp.route('/')
def liste_projets():
    
    projets = Projet.query.order_by(Projet.id_projet).all()  # SELECT * FROM projets ORDER BY projets.id_projets
    return render_template('projets.html', projets = projets)




# Les suppressions de projets ne pose pas de probleme pour  le moment mais il faudra faire attention au effet de cascade 
# On ne peut pas supprimer un client qui est déja relié à un projet (par sécurité)

@projets_bp.route('/supprimer_projet/<int:id>', methods=['POST'])
def  supprimer_projet(id): 
    print(id)
    try: 
        db.session.query(Projet).filter_by(id_projet=id).delete()
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        return jsonify ("erreur de ses morts :" + str(e))
    return redirect(url_for('projets.liste_projets'))



@projets_bp.route('/<int:id>' ,methods=['GET']) # Détail d'un projet
def detail_projet(id):
    projet = Projet.query.get_or_404(id)
    return render_template('detail_projet.html',projet = projet)
    


@projets_bp.route('/add' ,methods=['GET'])
def ajouter_projet_form():
    return render_template('ajouter_projet.html')


@projets_bp.route('/add' ,methods=['POST'])
def ajouter_projet_data():
    if request.is_json:
        projetData = request.get_json()
    else:
        projetData = request.form # pas de () c'est un attribut

    # On adapte la synthaxe pour quelle fonctionne avec postman et form

    nom = projetData.get("nom_projet")
    statut = projetData.get("statut_projet")
    date_debut = projetData.get("date_debut_projet"),
    date_fin = projetData.get("date_fin_projet"),

    try: 
        convention_id = int(projetData.get("id_convention"))
    except (ValueError, TypeError): 
        return jsonify({"erreur": "L'ID client ou convention doit être un nombre"}), 400

    
        
    nouveau_projet = Projet (
        nom_projet =  nom,
        statut_projet = statut,
        date_debut_projet = date_debut,
        date_fin_projet = date_fin,
        id_convention = convention_id
        ) 
    # On récupére les infos du nouveau projet dans la requete


    # de meme pour la creation dans la DB 
    try:
        db.session.add(nouveau_projet)
        db.session.commit()


    
        if request.is_json: 
            return jsonify({"message": "Succès ! Projet créé", "id": nouveau_projet.id_projet}), 201
        else:
            return redirect(url_for('projets.liste_projets'))

    except Exception as e:
        db.session.rollback()
        return jsonify({"erreur": str(e)}), 500
    



# on pourra editer un projet via un bouton sur détail projet et peut etre aussi
@projets_bp.route('/edit/<int:id>', methods=['GET'])
def modifier_projet_get(id):
    projet = Projet.query.get_or_404(id)
    return render_template('modifier_projet.html',projet=projet)


@projets_bp.route('/edit/<int:id>', methods=['POST'])
def modifier_projet_post(id):
    projet = Projet.query.get_or_404(id)
    
    
    if request.is_json:
        projetData = request.get_json()
    else:
        projetData = request.form # pas de () c'est un attribut
    
    # SQLalchmey vérifie automaiquement si les valeurs sont différentes donc on a seulement besoin de les modifier
    

    projet.nom_projet = projetData.get("nom_projet")
    projet.statut_projet = projetData.get("statut_projet")
    projet.date_debut_projet = projetData.get("date_debut_projet"),
    projet.date_fin_projet = projetData.get("date_fin_projet"),

    try: 
        projet.id_convention = int(projetData.get("id_convention"))
    except (ValueError, TypeError): 
        return jsonify({"erreur": "L'ID client ou convention doit être un nombre"}), 400

    try:
        db.session.commit()
        return redirect(url_for('projets.detail_projet', id=projet.id_projet))
    except Exception as e:
        db.session.rollback()
        return f"Erreur lors de la modification : {e}"
