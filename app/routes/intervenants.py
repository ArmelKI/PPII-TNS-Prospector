from flask import Blueprint, render_template, request, redirect, url_for
from app.models import Intervenant, db

intervenants_bp = Blueprint('intervenants', __name__)

# Route : Liste des intervenants
@intervenants_bp.route('/intervenants')
def liste_intervenants():
    intervenants = Intervenant.query.all()
    return render_template('intervenants.html', intervenants=intervenants)

# Route : Ajouter un intervenant
@intervenants_bp.route('/intervenant/add', methods=['GET', 'POST'])
def ajouter_intervenant():
    if request.method == 'POST':
        nom = request.form['nom']
        competences = request.form['competences']
        dispo = request.form['disponibilite']
        new_intervenant = Intervenant(nom=nom, competences=competences, disponibilite=dispo)
        db.session.add(new_intervenant)
        db.session.commit()
        return redirect(url_for('intervenants.liste_intervenants'))
    return render_template('ajouter_intervenant.html')

# Route : Modifier un intervenant
@intervenants_bp.route('/intervenant/edit/<int:id>', methods=['GET', 'POST'])
def modifier_intervenant(id):
    intervenant = Intervenant.query.get_or_404(id)

    if request.method == 'POST':
        intervenant.nom = request.form['nom']
        intervenant.competences = request.form['competences']
        intervenant.disponibilite = request.form['disponibilite']
        db.session.commit()
        return redirect(url_for('intervenants.liste_intervenants'))

    return render_template('modifier_intervenant.html', intervenant=intervenant)


# Route : Supprimer un intervenant
@intervenants_bp.route('/intervenant/delete/<int:id>', methods=['POST'])
def supprimer_intervenant(id):
    intervenant = Intervenant.query.get_or_404(id)
    db.session.delete(intervenant)
    db.session.commit()
    return redirect(url_for('intervenants.liste_intervenants'))

# Note: Les templates 'intervenants.html', 'ajouter_intervenant.html', et 'modifier_intervenant.html'
# doivent être créés dans le dossier 'templates' pour que ces routes fonctionnent correctement.

