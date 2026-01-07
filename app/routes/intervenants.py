import os
import secrets
import csv
from io import StringIO
from flask import Blueprint, render_template, request, redirect, url_for, flash, Response, current_app
from sqlalchemy.orm import joinedload
from werkzeug.utils import secure_filename
from app.models import Intervenant, Utilisateur, Competence, db, MaitriseCompetence
from flask_login import login_required
from app.permissions import manage_intervenants_required

intervenants_bp = Blueprint("intervenants", __name__, url_prefix="/intervenants")

def save_uploaded_file(file_obj, subfolder="documents"):
    """
    Saves a given file object to the app's static upload directory.

    Args:
        file_obj (FileStorage): The file object from request.files.
        subfolder (str): The specific subfolder inside 'static/uploads/' (e.g., 'avatars').

    Returns:
        str: The relative path to the saved file for database storage, or None if no file provided.
    """
    if not file_obj or file_obj.filename == '':
        return None

    original_name = secure_filename(file_obj.filename)

    # Generate a random hex string to append to filename to avoid overwrites
    random_hex = secrets.token_hex(4)
    name, ext = os.path.splitext(original_name)
    new_filename = f"{name}_{random_hex}{ext}"

    # Ensure the upload directory exists
    upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', subfolder)
    os.makedirs(upload_dir, exist_ok=True)

    # Save the file physically
    save_path = os.path.join(upload_dir, new_filename)
    file_obj.save(save_path)

    # Return relative path for DB
    return f"uploads/{subfolder}/{new_filename}"

@intervenants_bp.route("/", methods=["GET"])
@login_required
def liste_intervenants():
    """
    Displays a paginated list of all intervenants (contributors).
    Includes search functionality for names and skills, and filtering by availability.
    """
    search = request.args.get('search', '').strip()
    dispo = request.args.get('disponibilite', '')
    page = request.args.get('page', 1, type=int)
    per_page = 8

    # 1. Base Query construction
    # We join with Utilisateur to access names, and eager load skills to optimize performance.
    q = Intervenant.query.join(Utilisateur).options(
        joinedload(Intervenant.utilisateur),
        joinedload(Intervenant.maitrise_details).joinedload(MaitriseCompetence.competence)
    )

    # 2. Apply Search Filters
    # If a search term exists, we filter by User's First/Last Name OR Skill Name.
    if search:
        # Note: We use outerjoin to include intervenants even if they don't have skills yet,
        # but match the name search criteria.
        q = q.outerjoin(Intervenant.maitrise_details).outerjoin(MaitriseCompetence.competence).filter(
            (Utilisateur.nom_utilisateur.ilike(f"%{search}%")) |
            (Utilisateur.prenom_utilisateur.ilike(f"%{search}%")) |
            (Competence.nom_competence.ilike(f"%{search}%"))
        )

    # 3. Apply Availability Filter
    if dispo:
        dispo_bool = dispo.lower() == "disponible"
        # We explicitly filter on the Intervenant model to avoid ambiguity in joins
        q = q.filter(Intervenant.disponible == dispo_bool)

    # 4. Pagination
    # Fetch the results for the current page
    pagination = q.order_by(Utilisateur.nom_utilisateur).paginate(page=page, per_page=per_page, error_out=False)

    return render_template('intervenants.html', intervenants=pagination, search_query=search, filter_dispo=dispo)


@intervenants_bp.route('/add', methods=['GET', 'POST'])
@manage_intervenants_required
def ajouter_intervenant():
    """
    Handles the creation of a new intervenant profile.
    Can either link an existing User who isn't an intervenant yet, or create a brand new User.
    Also handles file uploads (CV, Photo) and Skills parsing.
    """
    if request.method == "POST":
        # --- 1. File Validation ---
        cv_file = request.files.get('cv_file')
        photo_file = request.files.get('photo_file')

        # Mandatory files check
        if not cv_file or cv_file.filename == '':
            flash("Le CV est obligatoire", "warning")
            return redirect(request.url)

        if not photo_file or photo_file.filename == '':
            flash("Le CV est obligatoire", "warning")
            return redirect(request.url)

        # --- 2. Form Data Retrieval ---
        id_util = request.form.get("id_utilisateur")
        prenom = request.form.get("prenom_utilisateur", "").strip()
        nom = request.form.get("nom_utilisateur", "").strip()
        email = request.form.get("email_utilisateur", "").strip()
        dispo = request.form.get("disponible") == "on"
        heures = request.form.get("heures", type=float, default=0.0)
        competences_raw = request.form.get("competences", "")

        # --- 3. User Handling ---
        if id_util:
            # Case A: Linking an existing user
            # Security check: Ensure this user isn't already an intervenant
            deja_intervenant = Intervenant.query.get(int(id_util))
            if deja_intervenant:
                flash(f"Error: The selected user is already an intervenant.", "danger")
                return redirect(url_for("intervenants.ajouter_intervenant"))

            utilisateur = Utilisateur.query.get(int(id_util))
        else:
            # Case B: Creating a new user from scratch
            if not (prenom and nom and email):
                flash("Please provide First Name, Last Name, and Email.", "warning")
                return redirect(url_for("intervenants.ajouter_intervenant"))

            utilisateur = Utilisateur(
                prenom_utilisateur=prenom,
                nom_utilisateur=nom,
                mail_utilisateur=email,
                permission=0,
                id_role=1 # Default role ID
            )
            # Set a temporary password (in production, send an invite email instead)
            utilisateur.set_password('pass')
            db.session.add(utilisateur)
            db.session.flush() # Flush to generate the ID needed for the Intervenant table

        # --- 4. File Saving ---
        path_cv = save_uploaded_file(cv_file, 'documents')
        path_photo = save_uploaded_file(photo_file, 'avatars')
        path_carte_etu = save_uploaded_file(request.files.get('carte_etu_file'), 'documents')
        path_carte_vitale = save_uploaded_file(request.files.get('carte_vitale_file'), 'documents')

        # --- 5. Create Intervenant Record ---
        intervenant = Intervenant(
            id_intervenant=utilisateur.id_utilisateur,
            disponible=dispo,
            nb_heures_dispo=heures,
            cv=path_cv,
            photo_identite=path_photo,
            carte_etudiante=path_carte_etu,
            carte_vitale=path_carte_vitale
        )

        # --- 6. Skills Parsing ---
        # Input format expected: "Python, 5; SQL, 3"
        items = [c.strip() for c in competences_raw.split(";") if c.strip()]

        for item in items:
            # Cleaning: remove parentheses to handle formats like "(Name, Score)"
            clean_item = item.replace("(", "").replace(")", "")
            parts = clean_item.split(",")
            cname = parts[0].strip()

            # Try to parse the score, default to 0 if missing or invalid
            note = 0
            if len(parts) > 1:
                try:
                    note = int(parts[1].strip())
                except ValueError:
                    note = 0

            # Boundary check for the score (0-10)
            if note > 10 or note < 0 :
                flash("Please enter a score out of 10 for each skill. Defaulted to 0.", "danger")
                note = 0

            if cname:
                # Check if skill exists in DB, create if not
                comp = Competence.query.filter(Competence.nom_competence.ilike(cname)).first()
                if not comp:
                    comp = Competence(nom_competence=cname)
                    db.session.add(comp)
                    db.session.flush() # Get ID for association

                # Create the link (Intervenant <-> Skill) with mastery level
                lien = MaitriseCompetence(intervenant=intervenant, competence=comp, niveau_maitrise=note)
                db.session.add(lien)

        db.session.add(intervenant)
        db.session.commit()

        flash("Intervenant successfully created!", "success")
        return redirect(url_for("intervenants.liste_intervenants"))

    # GET Request: Fetch users who are NOT yet intervenants to populate the dropdown
    utilisateurs_disponibles = Utilisateur.query\
    .outerjoin(Intervenant)\
    .filter(Intervenant.id_intervenant == None)\
    .order_by(Utilisateur.nom_utilisateur)\
    .all()

    return render_template("ajouter_intervenant.html", utilisateurs=utilisateurs_disponibles)


@intervenants_bp.route("/edit/<int:id>", methods=["GET", "POST"])
@manage_intervenants_required
def modifier_intervenant(id):
    """
    Updates an existing intervenant's profile (availability, files, skills).
    """
    intervenant = Intervenant.query.options(joinedload(Intervenant.utilisateur)).get_or_404(id)

    if request.method == "POST":
        # Update basic info
        intervenant.disponible = request.form.get("disponible") == "on"
        intervenant.nb_heures_dispo = request.form.get("heures", type=float, default=0.0)

        # Update files only if a new file is uploaded
        new_cv = save_uploaded_file(request.files.get('cv_file'), 'documents')
        if new_cv: intervenant.cv = new_cv

        new_photo = save_uploaded_file(request.files.get('photo_file'), 'avatars')
        if new_photo: intervenant.photo_identite = new_photo

        new_etu = save_uploaded_file(request.files.get('carte_etu_file'), 'documents')
        if new_etu: intervenant.carte_etudiante = new_etu

        new_vitale = save_uploaded_file(request.files.get('carte_vitale_file'), 'documents')
        if new_vitale: intervenant.carte_vitale = new_vitale

        # --- Skills Update Strategy ---
        # 1. We delete all existing skill links for this intervenant
        MaitriseCompetence.query.filter_by(id_intervenant=intervenant.id_intervenant).delete()

        # 2. We re-create them from the form input
        competences_raw = request.form.get("competences", "")
        items = [c.strip() for c in competences_raw.split(";") if c.strip()]

        for item in items:
            clean_item = item.replace("(", "").replace(")", "")
            parts = clean_item.split(",")
            cname = parts[0].strip()

            note = 0
            if len(parts) > 1:
                try:
                    note = int(parts[1].strip())
                except ValueError:
                    note = 0

            if note > 10 or note < 0 :
                flash("Please enter a score out of 10. Defaulted to 0.", "danger")
                note = 0

            if cname:
                comp = Competence.query.filter(Competence.nom_competence.ilike(cname)).first()
                if not comp:
                    comp = Competence(nom_competence=cname)
                    db.session.add(comp)
                    db.session.flush()

                lien = MaitriseCompetence(intervenant=intervenant, competence=comp, niveau_maitrise=note)
                db.session.add(lien)

        db.session.commit()
        flash("Profile updated successfully.", "info")
        return redirect(url_for("intervenants.liste_intervenants"))

    # GET: Pre-fill the form
    # We reconstruct the skills string format "(Name, Score); (Name, Score)" for the text input
    maitrises_existantes = MaitriseCompetence.query.filter_by(id_intervenant=intervenant.id_intervenant).all()
    competences_str = "; ".join([f"({m.competence.nom_competence}, {m.niveau_maitrise})" for m in maitrises_existantes])

    return render_template("modifier_intervenant.html", intervenant=intervenant, competences_str=competences_str)


@intervenants_bp.route("/delete/<int:id>", methods=["POST"])
@manage_intervenants_required
def supprimer_intervenant(id):
    """
    Deletes an intervenant profile.
    Note: This does NOT delete the associated User account, only the Intervenant role/data.
    """
    intervenant = Intervenant.query.get_or_404(id)
    db.session.delete(intervenant)
    db.session.commit()
    flash("Intervenant deleted.", "success")
    return redirect(url_for("intervenants.liste_intervenants"))


@intervenants_bp.route("/export", methods=["GET"])
@login_required
def exporter_intervenants():
    intervenants: list[Intervenant] = Intervenant.query.all()

    # Use StringIO to create an in-memory text buffer
    si = StringIO()
    writer = csv.writer(si)
    writer.writerow([
        "id_intervenant",
        "disponible",
        "nb_heures_dispo",
        "bulletin_adhesion",
        "carte_etudiante",
        "carte_vitale",
        "piece_identite",
        "photo_identite",
        "cv",
    ])
    for i in intervenants:
        writer.writerow([
            i.id_intervenant,
            i.disponible,
            i.nb_heures_dispo,
            i.bulletin_adhesion,
            i.carte_etudiante,
            i.carte_vitale,
            i.piece_identite,
            i.photo_identite,
            i.cv
        ])

    return Response(
        si.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=intervenants.csv"}
    )
