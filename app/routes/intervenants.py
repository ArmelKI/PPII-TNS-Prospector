from flask import Blueprint, render_template, request, redirect, url_for, flash, Response, current_app
from sqlalchemy.orm import joinedload
from app.models import Intervenant, Utilisateur, Competence, db
from io import StringIO
from sqlalchemy.orm import joinedload
import csv
import secrets

intervenants_bp = Blueprint("intervenants", __name__, url_prefix="/intervenants")

@intervenants_bp.route("/", methods=["GET"])
def liste_intervenants():
    search = request.args.get('search', '').strip()
    dispo = request.args.get('disponibilite', '')
    page = request.args.get('page', 1, type=int)
    per_page = 8

    q = Intervenant.query.options(joinedload(Intervenant.utilisateur), joinedload(Intervenant.competences))

    # XXX : Possible injection SQL !!!
    if search:
        q = q.join(Intervenant.utilisateur).outerjoin(Intervenant.competences).filter(
            (Utilisateur.nom_utilisateur.ilike(f"%{search}%")) |
            (Utilisateur.prenom_utilisateur.ilike(f"%{search}%")) |
            (Competence.nom_competence.ilike(f"%{search}%"))
        )

    if dispo:
        intervenants = intervenants.filter_by(disponibilite=dispo)

    pagination = q.order_by(Utilisateur.nom_utilisateur).paginate(page=page, per_page=per_page, error_out=False)

    return render_template('intervenants.html',
                           intervenants=pagination,
                           search_query=search,
                           filter_dispo=dispo)

# TODO corriger pour correspondre à l'E-R
# === Ajouter ===
@intervenants_bp.route('/add', methods=['GET', 'POST'])
def ajouter_intervenant():
    if request.method == "POST":
        # récupération formulaire
        id_util = request.form.get("id_utilisateur")  # optional: link existing user
        prenom = request.form.get("prenom_utilisateur", "").strip()
        nom = request.form.get("nom_utilisateur", "").strip()
        email = request.form.get("email_utilisateur", "").strip()
        dispo = request.form.get("disponible") == "on"
        heures = request.form.get("heures", type=float, default=0.0)
        competences_raw = request.form.get("competences", "")

        # si on attache un utilisateur existant
        if id_util:
            utilisateur = Utilisateur.query.get(int(id_util))
            if not utilisateur:
                flash("Utilisateur introuvable.", "danger")
                return redirect(url_for("intervenants.ajouter_intervenant"))
        else:
            # Création d'un utilisateur minimal : mdp_utilisateur doit être non-NULL selon ta BDD
            if not (prenom and nom and email):
                flash("Renseignez le prénom, le nom et l'email pour créer un utilisateur.", "warning")
                return redirect(url_for("intervenants.ajouter_intervenant"))

            # Génère un mot de passe temporaire sûr (stocké tel quel si vous n'avez pas encore hashing)
            # Si vous utilisez hashing ailleurs, remplacez par la fonction de hash correspondante.
            temp_password = secrets.token_urlsafe(12)

            utilisateur = Utilisateur(
                prenom_utilisateur=prenom,
                nom_utilisateur=nom,
                mail_utilisateur=email,
                mdp_utilisateur=temp_password,  # valeur non-NULL
                id_role=None
            )
            db.session.add(utilisateur)
            db.session.flush()  # obtient id_utilisateur

            # avertir en log (et en flash) que le mot de passe est temporaire
            current_app.logger.info("Utilisateur créé temporairement %s (%s) avec mdp temporaire.", email, utilisateur.id_utilisateur)
            flash(f"Utilisateur créé (mot de passe temporaire généré). Demandez à l'utilisateur de réinitialiser le mot de passe.", "info")

        # Crée l'intervenant (id_intervenant = id_utilisateur)
        intervenant = Intervenant(
            id_intervenant=utilisateur.id_utilisateur,
            disponible_actuellement=dispo,
            nombre_heures_disponibles=heures
        )

        # Gestion des compétences
        comps = [c.strip() for c in competences_raw.replace(",", ";").split(";") if c.strip()]
        for cname in comps:
            comp = Competence.query.filter(Competence.nom_competence.ilike(cname)).first()
            if not comp:
                comp = Competence(nom_competence=cname)
                db.session.add(comp)
                db.session.flush()
            intervenant.competences.append(comp)

        db.session.add(intervenant)
        db.session.commit()
        flash("Intervenant créé avec succès.", "success")
        return redirect(url_for("intervenants.liste_intervenants"))

    # GET : afficher formulaire, fournir liste d'utilisateurs existants pour lier si besoin
    utilisateurs = Utilisateur.query.order_by(Utilisateur.nom_utilisateur).all()
    return render_template("ajouter_intervenant.html", utilisateurs=utilisateurs)

# TODO A tester avec un dataset de test
@intervenants_bp.route("/edit/<int:id>", methods=["GET", "POST"])
def modifier_intervenant(id):
    intervenant = Intervenant.query.options(joinedload(Intervenant.utilisateur), joinedload(Intervenant.competences)).get_or_404(id)
    if request.method == "POST":
        intervenant.disponible_actuellement = request.form.get("disponible") == "on"
        intervenant.nombre_heures_disponibles = request.form.get("heures", type=float, default=intervenant.nombre_heures_disponibles)
        competences_raw = request.form.get("competences", "")
        comps = [c.strip() for c in competences_raw.replace(",", ";").split(";") if c.strip()]

        intervenant.competences = []
        for cname in comps:
            comp = Competence.query.filter(Competence.nom_competence.ilike(cname)).first()
            if not comp:
                comp = Competence(nom_competence=cname)
                db.session.add(comp)
                db.session.flush()
            intervenant.competences.append(comp)

        db.session.commit()
        flash("Modifications enregistrées.", "info")
        return redirect(url_for("intervenants.details_intervenant", id=intervenant.id_intervenant))

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
    intervenants = Intervenant.query.options(joinedload(Intervenant.utilisateur), joinedload(Intervenant.competences)).all()
    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(["ID", "Nom", "Prénom", "Email", "Compétences", "Disponible", "Heures"])
    for i in intervenants:
        nom = i.utilisateur.nom_utilisateur if i.utilisateur else ""
        prenom = i.utilisateur.prenom_utilisateur if i.utilisateur else ""
        email = i.utilisateur.mail_utilisateur if i.utilisateur else ""
        comps = ";".join([c.nom_competence for c in i.competences])
        writer.writerow([i.id_intervenant, nom, prenom, email, comps, i.disponible_actuellement, i.nombre_heures_disponibles])
    return Response(si.getvalue(), mimetype="text/csv", headers={"Content-Disposition": "attachment;filename=intervenants.csv"})
