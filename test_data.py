from datetime import date, timedelta

# --- MOCK CLASSES (Pour simuler tes Models SQLAlchemy sans la BDD) ---

class MockIntervenant:
    def __init__(self, id, nom, dispo_heures, skills_dict):
        self.id_intervenant = id
        self.nom = nom # Simule le lien avec Utilisateur
        self.nb_heures_dispo = dispo_heures
        self.disponible = True
        # On simplifie ici : au lieu d'une liste d'objets Competence, 
        # on met un dictionnaire {Nom: Niveau} pour faciliter le test
        self.competences = skills_dict 

    def __repr__(self):
        return f"<Intervenant {self.nom} ({self.nb_heures_dispo}h/sem)>"

class MockTache:
    def __init__(self, id, titre, skills_req, charge_totale, deadline_weeks):
        self.id_tache = id
        self.nom_tache = titre
        # Dictionnaire des besoins {NomCompetence: NiveauMinimum}
        self.competences_requises = skills_req 
        self.charge_estimee = charge_totale # En heures totales
        self.date_dernier_delai_tache = date.today() + timedelta(weeks=deadline_weeks)

    def __repr__(self):
        return f"<Mission {self.nom_tache} (Charge: {self.charge_estimee}h)>"

# --- GÉNÉRATEUR DE DONNÉES ---

def get_test_data():
    """
    Retourne deux listes : une liste d'intervenants et une liste de missions (tâches).
    Couvre des cas variés : experts, débutants, généralistes.
    """
    
    # 1. CRÉATION DES INTERVENANTS (Le "Pool")
    intervenants = [
        # --- PROFIL 1 : L'Expert Python (Mais peu dispo) ---
        MockIntervenant(
            id=1, 
            nom="Alice (Expert Python)", 
            dispo_heures=5,  # Très peu dispo
            skills_dict={"Python": 9, "Django": 8, "SQL": 7}
        ),

        # --- PROFIL 2 : Le Fullstack Web (Dispo moyenne) ---
        MockIntervenant(
            id=2, 
            nom="Bob (Web Dev)", 
            dispo_heures=15, 
            skills_dict={"React": 8, "Javascript": 8, "HTML/CSS": 9, "NodeJS": 7}
        ),

        # --- PROFIL 3 : Le Data Scientist (Très dispo) ---
        MockIntervenant(
            id=3, 
            nom="Charlie (Data)", 
            dispo_heures=25, 
            skills_dict={"Python": 7, "Pandas": 8, "Machine Learning": 7, "SQL": 8}
        ),

        # --- PROFIL 4 : Le DevOps (Profil rare) ---
        MockIntervenant(
            id=4, 
            nom="David (DevOps)", 
            dispo_heures=10, 
            skills_dict={"Docker": 8, "AWS": 7, "Linux": 8, "Python": 5}
        ),

        # --- PROFIL 5 : Le Junior Polyvalent (Niveau faible partout, mais motivé) ---
        MockIntervenant(
            id=5, 
            nom="Emma (Junior)", 
            dispo_heures=30, # Grosse dispo
            skills_dict={"Python": 3, "Java": 3, "Javascript": 4, "SQL": 3}
        ),
        
        # --- PROFIL 6 : Le Spécialiste Java (Fort en Java, nul ailleurs) ---
        MockIntervenant(
            id=6, 
            nom="Fabrice (Java Only)", 
            dispo_heures=20,
            skills_dict={"Java": 9, "Spring": 8}
        )
    ]

    # 2. CRÉATION DES MISSIONS (Les "Taches")
    missions = [
        # --- SCÉNARIO A : Mission Facile (Match avec presque tout le monde) ---
        MockTache(
            id=101,
            titre="Script Python simple",
            skills_req={"Python": 2}, # Niveau requis très bas
            charge_totale=10, # 10 heures de boulot
            deadline_weeks=2
        ),

        # --- SCÉNARIO B : Mission Web Standard (Match avec Bob) ---
        MockTache(
            id=102,
            titre="Site Vitrine React",
            skills_req={"React": 6, "HTML/CSS": 5},
            charge_totale=50,
            deadline_weeks=4
        ),

        # --- SCÉNARIO C : Mission Data Lourde (Besoin de Charlie ou Equipe Alice+Emma) ---
        MockTache(
            id=103,
            titre="Analyse de Données Clients",
            skills_req={"Python": 6, "SQL": 6, "Pandas": 5},
            charge_totale=100, # Grosse charge
            deadline_weeks=6
        ),

        # --- SCÉNARIO D : Mission Impossible (Niveau requis trop haut ou compétence inexistante) ---
        MockTache(
            id=104,
            titre="Migration Legacy COBOL",
            skills_req={"COBOL": 8}, # Personne n'a ça dans la liste
            charge_totale=200,
            deadline_weeks=8
        ),

        # --- SCÉNARIO E : Mission Complexe (Besoin d'équipe multidiscipline) ---
        MockTache(
            id=105,
            titre="Plateforme SaaS Complète",
            skills_req={"Python": 6, "React": 6, "Docker": 5}, # Besoin Backend + Frontend + DevOps
            charge_totale=150,
            deadline_weeks=10
        )
    ]

    return intervenants, missions

# --- EXEMPLE D'UTILISATION ---
if __name__ == "__main__":
    pool, tasks = get_test_data()
    print(f"Généré {len(pool)} intervenants et {len(tasks)} missions pour le test.")
    
    # Exemple d'accès
    print(f"Compétences de {pool[0].nom}: {pool[0].competences}")
    print(f"Besoins pour {tasks[1].nom_tache}: {tasks[1].competences_requises}")