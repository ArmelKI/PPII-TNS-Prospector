import random
from datetime import date, timedelta
from app import create_app
from app.models import (
    db, Client, Utilisateur, Intervenant, Competence, Projet, Convention,
    Jalon, Role, StatutProjet, StatutJalon, Tache, StatutTache,
    EtatRelation, InteractionClient, MaitriseCompetence
)
from app.permissions import all_perms

app = create_app(testing=False)

with app.app_context():
    print("🗑  Wiping and resetting the database...")
    db.session.remove()
    db.engine.dispose()

    # On utilise CASCADE pour forcer la suppression malgré les clés étrangères
    db.metadata.reflect(bind=db.engine)
    db.drop_all()
    db.create_all()

    # --- 1. Roles & Relationship States ---
    print("⚙️  Setting up roles and relationship states...")

    r_admin = Role(nom_role="Administrateur")  # type: ignore ; Admin role for privileged users
    r_inter = Role(nom_role="Intervenant")     #  type: ignore ; Regular team member role
    db.session.add_all([r_admin, r_inter])

    rel_prospect = EtatRelation(libelle_relation="Prospect")         # type: ignore ; Potential client
    rel_client = EtatRelation(libelle_relation="Client Actif")       # type: ignore ; Active client
    rel_ancien = EtatRelation(libelle_relation="Ancien Client")      # type: ignore ; Former client
    db.session.add_all([rel_prospect, rel_client, rel_ancien])
    db.session.commit()

    # --- 3. Users / Team Members ---
    print("👥 Creating admin account...")

    admin = Utilisateur(prenom_utilisateur="Admin", nom_utilisateur="Admin", mail_utilisateur="admin", permission=all_perms, id_role=1, mdp_utilisateur = "$2b$12$tgFWQzanVpp8MO9CGlV45ulmkjtPD2iSMmWN5RFRxzOAB1UAdvXeq")
    db.session.add(admin)
    db.session.commit()

    print("✅ Database successfully reloaded! (Interactions, Teams, Kanban, Clients)")
