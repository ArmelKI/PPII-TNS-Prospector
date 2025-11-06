from flask import Blueprint, render_template, request, redirect, url_for, Response, flash
from app.models import Intervenant, db
import csv
from io import StringIO
from sqlalchemy.orm import joinedload

intervenants = db.session.query(Intervenant).options(joinedload(Intervenant.utilisateur)).all()


intervenants_bp = Blueprint('intervenants', __name__)

# === Liste avec recherche, filtre et pagination ===
@intervenants_bp.route('/intervenants')
def liste_intervenants():
    query = request.args.get('q', '')
    dispo = request.args.get('disponible_actuellement', '')
    page = request.args.get('page', 1, type=int)
    per_page = 5

    intervenants = Intervenant.query

    if query:
        intervenants = intervenants.filter(
            (Intervenant.utilisateur.nom_utilisateur.contains(query)) | 
            (Intervenant.competences.contains(query))
        )
    if dispo:
        intervenants = intervenants.filter_by(disponible_acutellement=dispo)

    intervenants = intervenants.order_by(Intervenant.utilisateur.nom_utilisateur).paginate(page=page, per_page=per_page, error_out=False)

    return render_template('intervenants.html',
                           intervenants=intervenants,
                           search_query=query,
                           filter_dispo=dispo)

# === Ajouter ===
@intervenants_bp.route('/intervenant/add', methods=['GET', 'POST'])
def ajouter_intervenant():
    if request.method == 'POST':
        nom = request.form['nom_utilisateur']
        competences = request.form['competences']
        dispo = request.form['disponible_actuellement']

        new_intervenant = Intervenant(utilisateur=nom, competences=competences, disponible_actuellement=dispo)
        db.session.add(new_intervenant)
        db.session.commit()
        flash("✅ Intervenant ajouté avec succès !", "success")
        return redirect(url_for('intervenants.liste_intervenants'))

    return render_template('ajouter_intervenant.html')

# === Modifier ===
@intervenants_bp.route('/intervenant/edit/<int:id>', methods=['GET', 'POST'])
def modifier_intervenant(id):
    intervenant = Intervenant.query.get_or_404(id)

    if request.method == 'POST':
        intervenant.utilisateur.nom_utilisateur = request.form['nom_utilisateur']
        intervenant.competences = request.form['competences']
        intervenant.disponible_actuellement = request.form['disponible_actuellement']
        db.session.commit()
        flash("✏️ Modifications enregistrées.", "info")
        return redirect(url_for('intervenants.liste_intervenants'))

    return render_template('modifier_intervenant.html', intervenant=intervenant)

# === Supprimer ===
@intervenants_bp.route('/intervenant/delete/<int:id>', methods=['POST'])
def supprimer_intervenant(id):
    intervenant = Intervenant.query.get_or_404(id)
    db.session.delete(intervenant)
    db.session.commit()
    flash("🗑 Intervenant supprimé avec succès.", "danger")
    return redirect(url_for('intervenants.liste_intervenants'))

# === Détails ===
@intervenants_bp.route('/intervenant/<int:id>')
def details_intervenant(id):
    intervenant = Intervenant.query.get_or_404(id)
    return render_template('details_intervenant.html', intervenant=intervenant)

# === Export CSV ===
@intervenants_bp.route('/intervenants/export')
def exporter_intervenants():
    intervenants = Intervenant.query.all()
    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(['ID', 'Nom', 'Compétences', 'Disponibilité'])
    for i in intervenants:
        writer.writerow([i.id_intervenant, i.utilisateur.nom_utilisateur, i.competences, i.disponible_actuellement])

    output = si.getvalue()
    return Response(
        output,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment;filename=intervenants.csv'}
    )
