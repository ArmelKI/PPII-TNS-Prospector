import random
from datetime import date, timedelta
from app import create_app
from app.models import (
    db, Client, Utilisateur, Intervenant, Competence, Projet, Convention,
    Jalon, Role, StatutProjet, StatutJalon, Tache, StatutTache,
    EtatRelation, InteractionClient, MaitriseCompetence
)

app = create_app()

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

    # --- 2. Skills / Competencies ---
    comps_list = [
        "Python", "React", "Vue.js", "Docker", "Figma", "Marketing",
        "SEO", "Droit", "Compta", "Java", "Angular"
    ]
    db_comps = []
    for c_name in comps_list:
        c = Competence(nom_competence=c_name)  # type: ignore ; Create a skill entry
        db.session.add(c)
        db_comps.append(c)
    db.session.commit()

    # --- 3. Users / Team Members ---
    print("👥 Creating 20 team members with diverse profiles...")

    prenoms = [
        "Lucas", "Julie", "Omar", "Sarah", "Thomas", "Emma", "Nathan", "Léa", "Enzo", "Chloé",
        "Gabriel", "Inès", "Leo", "Manon", "Paul", "Axel", "Camille", "Yasmine", "Theo", "Louise"
    ]
    noms = [
        "Martin", "Bernard", "Thomas", "Petit", "Robert", "Richard", "Durand", "Dubois", "Moreau", "Laurent",
        "Simon", "Michel", "Garcia", "David", "Bertrand", "Roux", "Blanc", "Guerin", "Boyer", "Andre"
    ]

    intervenants_objs = []

    # UNE SEULE BOUCLE ICI
    for i in range(len(prenoms)):
        u = Utilisateur()
        u.prenom_utilisateur = prenoms[i]
        u.nom_utilisateur = noms[i]
        u.mail_utilisateur = f"{prenoms[i].lower()}.{noms[i].lower()}@tns.fr"
        u.mdp_utilisateur = "$2b$12$tgFWQzanVpp8MO9CGlV45ulmkjtPD2iSMmWN5RFRxzOAB1UAdvXeq"
        u.id_role = r_inter.id_role

        db.session.add(u)
        db.session.flush()  # Crée l'ID utilisateur pour l'étape suivante

        est_dispo = (random.random() > 0.4)
        inter = Intervenant(
            id_intervenant=u.id_utilisateur,
            disponible=est_dispo,
            nb_heures_dispo=random.choice([5, 10, 15, 20, 25]) if est_dispo else 0,
            cv="uploads/documents/dummy.pdf",
            photo_identite="",
            carte_etudiante="",
            carte_vitale=""
        )

        db.session.add(inter)
        db.session.flush()  # Crée l'intervenant pour permettre la liaison compétences
        intervenants_objs.append(inter)

        # Assigner 1-4 compétences au hasard
        selected_comps = random.sample(db_comps, k=random.randint(1, 4))
        for comp in selected_comps:
            maitrise = MaitriseCompetence(
                id_intervenant=inter.id_intervenant,
                id_competence=comp.id_competence,
                niveau_maitrise=random.randint(1, 10)
            )
            db.session.add(maitrise)

    db.session.commit() # On valide tout le groupe d'utilisateurs

    # --- 4. Clients & Interactions ---
    print("🏢 Creating clients and their interaction history...")

    clients_data = [
        ("TotalEnergies", "Energie"), ("Sanofi", "Santé"), ("LVMH", "Luxe"),
        ("Airbus", "Aéronautique"), ("BNP Paribas", "Banque"), ("Orange", "Télécom"),
        ("Google France", "Tech"), ("Carrefour", "Retail"), ("SNCF", "Transport"), ("Decathlon", "Sport")
    ]

    types_interaction = [
        "Follow-up phone call", "Business lunch", "Sales presentation",
        "Quote sent", "Price negotiation", "Kickoff meeting",
        "Reminder email", "Contract signed", "Monthly progress review"
    ]

    for nom_cli, secteur in clients_data:
        c = Client(
            id_client=None,
            raison_sociale=nom_cli,
            secteur=secteur,
            mail_client=f"contact@{nom_cli.lower().replace(' ', '')}.com",
            telephone_client=f"01{random.randint(10,99)}{random.randint(10,99)}{random.randint(10,99)}{random.randint(10,99)}",
            date_dernier_contact=date.today() - timedelta(days=random.randint(0, 10)),
            latitude=48.8566 + (random.random() - 0.5) * 0.1,
            longitude=2.3522 + (random.random() - 0.5) * 0.1
        )
        db.session.add(c)
        db.session.flush()  # Get client ID for linking

        # Add 3-8 random interactions for each client
        for _ in range(random.randint(3, 8)):
            interact = InteractionClient(
                id_client=c.id_client, # type: ignore
                id_etat_relation=rel_client.id_etat_relation, # type: ignore
                date_interaction=date.today() - timedelta(days=random.randint(0, 60)), # type: ignore
                detail_interaction=random.choice(types_interaction) # type: ignore
            )
            db.session.add(interact)

        # Create a contract for the client
        conv = Convention(
            id_client=c.id_client, # type: ignore
            type_convention="CC", # type: ignore
            date_debut_convention=date.today(), # type: ignore
            prix=random.randint(5000, 45000) # type: ignore
        )
        db.session.add(conv)
        db.session.flush()  # Get convention ID for linking

        # Randomly pick a project status, favoring "in progress"
        statut_choisi = random.choice([
            StatutProjet.EN_COURS, StatutProjet.EN_COURS,
            StatutProjet.TERMINE, StatutProjet.BLOQUE
        ])
        # Randomly choose the start and end of a project 
        d_debut = date.today() - timedelta(days=random.randint(10,120))
        
        if statut_choisi == StatutProjet.TERMINE: 
            jours_ecoules = (date.today() - d_debut).days
            d_fin = d_debut + timedelta(days=random.randint(1,jours_ecoules))
        else :
            d_fin =date.today() + timedelta(weeks=random.randint(4,24))
        
        p = Projet(
            nom_projet=f"Mission {secteur} - {nom_cli}", # type: ignore
            statut_projet=statut_choisi, # type: ignore
            charge_projet=random.randint(20,300), # charge total  du projet entre 20 et 300 heures
            date_debut_projet=d_debut,
            date_fin_projet=d_fin, # type: ignore
            id_convention=conv.id_convention # type: ignore
        )

        # Assign a random team of 2-3 members to the project
        team = random.sample(intervenants_objs, k=random.randint(2, 3))
        for member in team:
            p.intervenants.append(member)

        # Attribution de 2 à 4 compétences requises au hasard
        besoins_techniques = random.sample(db_comps, k=random.randint(2, 4))
        for competence in besoins_techniques:
            p.competences_requises.append(competence)

        db.session.add(p)
        db.session.flush()  # Get project ID for linking

        # --- Kanban Board: Project Milestones ---
        etapes = [
            "Scoping", "UX/UI Mockup", "Backend Development",
            "Frontend Development", "Testing", "Production Release"
        ]
        for etape in etapes:
            rand = random.random()
            if rand < 0.4:
                st = StatutJalon.PASSE      # Milestone completed
            elif rand < 0.7:
                st = StatutJalon.ACTUEL     # Current milestone
            else:
                st = StatutJalon.A_VENIR    # Upcoming milestone

            j = Jalon(
                nom_jalon=etape, # type: ignore
                statut_jalon=st, # type: ignore
                id_projet=p.id_projet, # type: ignore
                date_fin_jalon=date.today() + timedelta(days=random.randint(-10, 40)) # type: ignore
            )
            db.session.add(j)
            db.session.flush()  # Ensure j.id_jalon is available

            # Add a sample task for each milestone, assigned to the first team member
            t = Tache(
                nom_tache=f"Do {etape}", # type: ignore
                description_tache="Technical task", # type: ignore
                statut_tache=StatutTache.EN_COURS, # type: ignore
                date_dernier_delai_tache=date.today() + timedelta(days=5), # type: ignore
                id_jalon=j.id_jalon, # type: ignore
                id_intervenant_tache=team[0].id_intervenant # type: ignore
            )
            db.session.add(t)

    db.session.commit()
    print("✅ Database successfully reloaded! (Interactions, Teams, Kanban, Clients)")
