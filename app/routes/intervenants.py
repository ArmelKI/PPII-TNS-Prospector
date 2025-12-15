import os
import secrets
import csv
from io import StringIO
from flask import Blueprint, render_template, request, redirect, url_for, flash, Response, current_app
from sqlalchemy.orm import joinedload
from werkzeug.utils import secure_filename
from app.models import Intervenant, Utilisateur, Competence, db

intervenants_bp = Blueprint("intervenants", __name__, url_prefix="/intervenants")

# --- Helper Function for Uploads ---
def save_uploaded_file(file_obj, subfolder="documents"):
    """
    Saves a file to app/static/uploads/<subfolder>/ and returns the relative path.
    Returns None if no file is provided.
    """
    if not file_obj or file_obj.filename == '':
        return None
    
    # 1. Secure the filename
    original_name = secure_filename(file_obj.filename)
    
    # 2. Generate unique name to prevent overwrite
    random_hex = secrets.token_hex(4)
    name, ext = os.path.splitext(original_name)
    new_filename = f"{name}_{random_hex}{ext}"
    
    # 3. Define path (app/static/uploads/...)
    upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', subfolder)
    os.makedirs(upload_dir, exist_ok=True)
    
    # 4. Save
    save_path = os.path.join(upload_dir, new_filename)
    file_obj.save(save_path)
    
    # 5. Return relative path for DB
    return f"uploads/{subfolder}/{new_filename}"


# --- Routes ---

@intervenants_bp.route("/", methods=["GET"])
def liste_intervenants():
    search = request.args.get('search', '').strip()
    dispo = request.args.get('disponibilite', '')
    page = request.args.get('page', 1, type=int)
    per_page = 8

    q = Intervenant.query.options(
        joinedload(Intervenant.utilisateur), # type: ignore
        joinedload(Intervenant.competences)  # type: ignore
    )

    if search:
        q = q.join(Utilisateur).outerjoin(Intervenant.competences).filter( # type: ignore
            (Utilisateur.nom_utilisateur.ilike(f"%{search}%")) |
            (Utilisateur.prenom_utilisateur.ilike(f"%{search}%")) |
            (Competence.nom_competence.ilike(f"%{search}%")) # type: ignore
        )

    if dispo:
        dispo_bool = dispo.lower() == "disponible"
        q = q.filter_by(disponible=dispo_bool)

    pagination = q.order_by(Utilisateur.nom_utilisateur).paginate(page=page, per_page=per_page, error_out=False)

    return render_template('intervenants.html', intervenants=pagination, search_query=search, filter_dispo=dispo)


@intervenants_bp.route('/add', methods=['GET', 'POST'])
def ajouter_intervenant():
    if request.method == "POST":
        # 1. Validation des champs obligatoires (Documents)
        # On vérifie que les fichiers sont bien présents dans la requête
        cv_file = request.files.get('cv_file')
        photo_file = request.files.get('photo_file')
        
        # Si l'un des fichiers majeurs manque, on bloque.
        if not cv_file or cv_file.filename == '':
            flash("Erreur : Le CV est obligatoire pour créer un profil.", "warning")
            return redirect(request.url) # Recharge la page avec l'erreur
            
        if not photo_file or photo_file.filename == '':
            flash("Erreur : La photo d'identité est obligatoire.", "warning")
            return redirect(request.url)

        # 2. Récupération des données texte
        id_util = request.form.get("id_utilisateur")
        prenom = request.form.get("prenom_utilisateur", "").strip()
        nom = request.form.get("nom_utilisateur", "").strip()
        email = request.form.get("email_utilisateur", "").strip()
        dispo = request.form.get("disponible") == "on"
        heures = request.form.get("heures", type=float, default=0.0)
        competences_raw = request.form.get("competences", "")

        # 3. Gestion Utilisateur
        if id_util:
            utilisateur = Utilisateur.query.get(int(id_util))
        else:
            if not (prenom and nom and email):
                flash("Veuillez renseigner Nom, Prénom et Email.", "warning")
                return redirect(url_for("intervenants.ajouter_intervenant"))

            temp_password = secrets.token_urlsafe(12)
            utilisateur = Utilisateur(
                prenom_utilisateur=prenom, # type: ignore
                nom_utilisateur=nom,       # type: ignore
                mail_utilisateur=email,    # type: ignore
                mdp_utilisateur=temp_password, # type: ignore
                id_role=1  # type: ignore
            )
            db.session.add(utilisateur)
            db.session.flush()

        # 4. Sauvegarde des fichiers
        path_cv = save_uploaded_file(cv_file, 'documents')
        path_photo = save_uploaded_file(photo_file, 'avatars')
        path_carte_etu = save_uploaded_file(request.files.get('carte_etu_file'), 'documents')
        path_carte_vitale = save_uploaded_file(request.files.get('carte_vitale_file'), 'documents')

        # 5. Création Intervenant
        intervenant = Intervenant(
            id_intervenant=utilisateur.id_utilisateur, # type: ignore
            disponible=dispo, # type: ignore
            nb_heures_dispo=heures, # type: ignore
            cv=path_cv, # type: ignore
            photo_identite=path_photo, # type: ignore
            carte_etudiante=path_carte_etu, # type: ignore
            carte_vitale=path_carte_vitale # type: ignore
        )

        # 6. Compétences
        comps = [c.strip() for c in competences_raw.replace(",", ";").split(";") if c.strip()]
        for cname in comps:
            comp = Competence.query.filter(Competence.nom_competence.ilike(cname)).first() # type: ignore
            if not comp:
                comp = Competence(nom_competence=cname) # type: ignore
                db.session.add(comp)
            intervenant.competences.append(comp)

        db.session.add(intervenant)
        db.session.commit()
        
        flash("Intervenant créé avec succès !", "success")
        return redirect(url_for("intervenants.liste_intervenants"))

    utilisateurs = Utilisateur.query.order_by(Utilisateur.nom_utilisateur).all()
    return render_template("ajouter_intervenant.html", utilisateurs=utilisateurs)


@intervenants_bp.route("/edit/<int:id>", methods=["GET", "POST"])
def modifier_intervenant(id):
    intervenant = Intervenant.query.options(joinedload(Intervenant.utilisateur)).get_or_404(id) # type: ignore
    
    if request.method == "POST":
        intervenant.disponible = request.form.get("disponible") == "on"
        intervenant.nb_heures_dispo = request.form.get("heures", type=float, default=0.0)
        
        # Mise à jour fichiers (seulement si un nouveau est envoyé)
        new_cv = save_uploaded_file(request.files.get('cv_file'), 'documents')
        if new_cv: intervenant.cv = new_cv # type: ignore
            
        new_photo = save_uploaded_file(request.files.get('photo_file'), 'avatars')
        if new_photo: intervenant.photo_identite = new_photo # type: ignore

        new_etu = save_uploaded_file(request.files.get('carte_etu_file'), 'documents')
        if new_etu: intervenant.carte_etudiante = new_etu # type: ignore

        new_vitale = save_uploaded_file(request.files.get('carte_vitale_file'), 'documents')
        if new_vitale: intervenant.carte_vitale = new_vitale # type: ignore

        # Compétences (Reset & Add)
        competences_raw = request.form.get("competences", "")
        comps = [c.strip() for c in competences_raw.replace(",", ";").split(";") if c.strip()]
        intervenant.competences = []
        for cname in comps:
            comp = Competence.query.filter(Competence.nom_competence.ilike(cname)).first() # type: ignore
            if not comp:
                comp = Competence(nom_competence=cname) # type: ignore
                db.session.add(comp)
            intervenant.competences.append(comp)

        db.session.commit()
        flash("Profil mis à jour.", "info")
        return redirect(url_for("intervenants.liste_intervenants"))

    competences_str = "; ".join([c.nom_competence for c in intervenant.competences])
    return render_template("modifier_intervenant.html", intervenant=intervenant, competences_str=competences_str)


@intervenants_bp.route("/delete/<int:id>", methods=["POST"])
def supprimer_intervenant(id):
    intervenant = Intervenant.query.get_or_404(id)
    db.session.delete(intervenant)
    db.session.commit()
    flash("Intervenant supprimé.", "danger")
    return redirect(url_for("intervenants.liste_intervenants"))


@intervenants_bp.route("/export", methods=["GET"])
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