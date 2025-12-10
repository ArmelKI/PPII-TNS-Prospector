
from flask import render_template, url_for, Blueprint# url_for  pour ajouter un projet , Blueprint pour les routes
from app.models import Projet 


projets_bp = Blueprint('projets',__name__,url_prefix="/projets")

@projets_bp.route('/')
def liste_projets():
    
    projets = Projet.query.all()  # SELECT * FROM projets


    
    return render_template('projets.html', projets = projets)

@projets_bp.route('/<int:id>' ,methods=['GET']) # Détail d'un projet
def detail_projet(id):
    projet = Projet.query.get_or_404(id)
    return render_template('detail_projet.html',projet = projet)
    
@projets_bp.route('/add' ,methods=['GET'])
def ajouter_projet():
    return render_template('ajouter_projet.html')

@projets_bp.route('/edit/<int:id>', methods=['GET'])
def modifier_projet():
    pass