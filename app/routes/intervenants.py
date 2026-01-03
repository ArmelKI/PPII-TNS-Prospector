import os
import secrets
import csv
from io import StringIO
from flask import Blueprint, render_template, request, redirect, url_for, flash, Response, current_app
from sqlalchemy.orm import joinedload
from werkzeug.utils import secure_filename
from app.models import Intervenant, Utilisateur, Competence, db, MaitriseCompetence
from app.matching import  call_ai_matching, create_ai_prompt
from flask_login import login_required

intervenants_bp = Blueprint("intervenants", __name__, url_prefix="/intervenants")

def save_uploaded_file(file_obj, subfolder="documents"):
    """
    Saves a file to app/static/uploads/<subfolder>/ and returns the relative path.
    Returns None if no file is provided.
    """
    if not file_obj or file_obj.filename == '':
        return None

    original_name = secure_filename(file_obj.filename)

    random_hex = secrets.token_hex(4)
    name, ext = os.path.splitext(original_name)
    new_filename = f"{name}_{random_hex}{ext}"

    upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', subfolder)
    os.makedirs(upload_dir, exist_ok=True)

    save_path = os.path.join(upload_dir, new_filename)
    file_obj.save(save_path)

    return f"uploads/{subfolder}/{new_filename}"

@intervenants_bp.route("/", methods=["GET"])
@login_required
def liste_intervenants():
    search = request.args.get('search', '').strip()
    dispo = request.args.get('disponibilite', '')
    page = request.args.get('page', 1, type=int)
    per_page = 8

    # 1. Base query
    q = Intervenant.query.join(Utilisateur).options(
        joinedload(Intervenant.utilisateur),
        joinedload(Intervenant.maitrise_details).joinedload(MaitriseCompetence.competence)
    )

    # 2. Search filters
    if search:
        q = q.outerjoin(Intervenant.maitrise_details).outerjoin(MaitriseCompetence.competence).filter(
            (Utilisateur.nom_utilisateur.ilike(f"%{search}%")) |
            (Utilisateur.prenom_utilisateur.ilike(f"%{search}%")) |
            (Competence.nom_competence.ilike(f"%{search}%"))
        )
    # 3. Availability filter
    if dispo:
        dispo_bool = dispo.lower() == "disponible"
        q = q.filter_by(disponible=dispo_bool)
    # 4. Pagination
    pagination = q.order_by(Utilisateur.nom_utilisateur).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('intervenants.html', intervenants=pagination, search_query=search, filter_dispo=dispo)


@intervenants_bp.route('/add', methods=['GET', 'POST'])
@login_required
def ajouter_intervenant():
    if request.method == "POST":
        # Check that files are present in the request
        cv_file = request.files.get('cv_file')
        photo_file = request.files.get('photo_file')

        # If one of the required files is missing, block the process.
        if not cv_file or cv_file.filename == '':
            flash("Erreur : Le CV est obligatoire pour créer un profil.", "warning")
            return redirect(request.url) # Reload the page with the error

        if not photo_file or photo_file.filename == '':
            flash("Erreur : La photo d'identité est obligatoire.", "warning")
            return redirect(request.url)

        id_util = request.form.get("id_utilisateur")
        prenom = request.form.get("prenom_utilisateur", "").strip()
        nom = request.form.get("nom_utilisateur", "").strip()
        email = request.form.get("email_utilisateur", "").strip()
        dispo = request.form.get("disponible") == "on"
        heures = request.form.get("heures", type=float, default=0.0)
        competences_raw = request.form.get("competences", "")

        if id_util:
            utilisateur = Utilisateur.query.get(int(id_util))
        else:
            if not (prenom and nom and email):
                flash("Veuillez renseigner Nom, Prénom et Email.", "warning")
                return redirect(url_for("intervenants.ajouter_intervenant"))

            temp_password = secrets.token_urlsafe(12)
            utilisateur = Utilisateur(
                prenom_utilisateur=prenom,
                nom_utilisateur=nom,
                mail_utilisateur=email,
                mdp_utilisateur=temp_password,
                id_role=1
            )
            db.session.add(utilisateur)
            db.session.flush()
        path_cv = save_uploaded_file(cv_file, 'documents')
        path_photo = save_uploaded_file(photo_file, 'avatars')
        path_carte_etu = save_uploaded_file(request.files.get('carte_etu_file'), 'documents')
        path_carte_vitale = save_uploaded_file(request.files.get('carte_vitale_file'), 'documents')

        intervenant = Intervenant(
            id_intervenant=utilisateur.id_utilisateur,
            disponible=dispo,
            nb_heures_dispo=heures,
            cv=path_cv,
            photo_identite=path_photo,
            carte_etudiante=path_carte_etu,
            carte_vitale=path_carte_vitale
        )

        comps = [c.strip() for c in competences_raw.replace(",", ";").split(";") if c.strip()]
        for cname in comps:
            comp = Competence.query.filter(Competence.nom_competence.ilike(cname)).first()
            if not comp:
                comp = Competence(nom_competence=cname)
                db.session.add(comp)
                db.session.flush()

            lien = MaitriseCompetence(
            intervenant=intervenant,
            competence=comp,
            niveau_maitrise=0)
            db.session.add(lien)

        db.session.add(intervenant)
        db.session.commit()

        flash("Intervenant créé avec succès !", "success")
        return redirect(url_for("intervenants.liste_intervenants"))
    
   
    utilisateurs = Utilisateur.query.order_by(Utilisateur.nom_utilisateur).all()
    return render_template("ajouter_intervenant.html", utilisateurs=utilisateurs)


@intervenants_bp.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def modifier_intervenant(id):
    intervenant = Intervenant.query.options(joinedload(Intervenant.utilisateur)).get_or_404(id) # type: ignore

    if request.method == "POST":
        intervenant.disponible = request.form.get("disponible") == "on"
        intervenant.nb_heures_dispo = request.form.get("heures", type=float, default=0.0)

        # Update files (only if a new one is sent)
        new_cv = save_uploaded_file(request.files.get('cv_file'), 'documents')
        if new_cv: intervenant.cv = new_cv

        new_photo = save_uploaded_file(request.files.get('photo_file'), 'avatars')
        if new_photo: intervenant.photo_identite = new_photo

        new_etu = save_uploaded_file(request.files.get('carte_etu_file'), 'documents')
        if new_etu: intervenant.carte_etudiante = new_etu

        new_vitale = save_uploaded_file(request.files.get('carte_vitale_file'), 'documents')
        if new_vitale: intervenant.carte_vitale = new_vitale

        
        competences_raw = request.form.get("competences", "")
        
        
        MaitriseCompetence.query.filter_by(id_intervenant=intervenant.id_intervenant).delete()
        
        
        items = [c.strip() for c in competences_raw.split(";") if c.strip()]
        
        for item in items:
            # Cleaning: remove parentheses to get "Name, Score"
            clean_item = item.replace("(", "").replace(")", "")
            parts = clean_item.split(",")
            cname = parts[0].strip()
            
            # Try to get the score (second part), otherwise 0 by default
            note = 0
            if len(parts) > 1:
                try:
                    note = int(parts[1].strip()) # or float() if you accept decimals
                except ValueError:
                    note = 0
            if note > 10 or note < 0 : # Input safety
                flash("Veuiller rentrer une note sur 10 pour chaque compétence, mis à 0 par défaut","danger") 
                note = 0
                

            if cname: 
                comp = Competence.query.filter(Competence.nom_competence.ilike(cname)).first() # type: ignore
                if not comp:
                    comp = Competence(nom_competence=cname)
                    db.session.add(comp)
                    db.session.flush()
                
                lien = MaitriseCompetence(intervenant=intervenant, competence=comp, niveau_maitrise=note)
                db.session.add(lien)

        db.session.commit()
        flash("Profil mis à jour.", "info")
        return redirect(url_for("intervenants.liste_intervenants"))

    
    maitrises_existantes = MaitriseCompetence.query.filter_by(id_intervenant=intervenant.id_intervenant).all()

    # Rebuild the string in the format "(Name, Score); (Name, Score)"
    competences_str = "; ".join([f"({m.competence.nom_competence}, {m.niveau_maitrise})" for m in maitrises_existantes])

    return render_template("modifier_intervenant.html", intervenant=intervenant, competences_str=competences_str)


@intervenants_bp.route("/delete/<int:id>", methods=["POST"])
@login_required
def supprimer_intervenant(id):
    intervenant = Intervenant.query.get_or_404(id)
    db.session.delete(intervenant)
    db.session.commit()
    flash("Intervenant supprimé.", "danger")
    return redirect(url_for("intervenants.liste_intervenants"))


@intervenants_bp.route("/export", methods=["GET"])
@login_required
def exporter_intervenants():
    intervenants = Intervenant.query.options(joinedload(Intervenant.utilisateur)).all() # type: ignore
    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(["ID", "Nom", "Prénom", "Email", "Compétences", "Disponible", "Heures", "CV"])
    for i in intervenants:
        u = i.utilisateur
        writer.writerow([
            i.id_intervenant, u.nom_utilisateur if u else "", u.prenom_utilisateur if u else "", u.mail_utilisateur if u else "",
            ";".join([c.nom_competence for c in i.competences]), i.disponible, i.nb_heures_dispo, i.cv
        ])
    return Response(si.getvalue(), mimetype="text/csv", headers={"Content-Disposition": "attachment;filename=intervenants.csv"})
