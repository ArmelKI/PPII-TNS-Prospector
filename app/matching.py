

########## INTERFACE CALL API IA ####################


from dotenv import load_dotenv
import os
import requests
import json

load_dotenv()

def create_ai_prompt(mission,intervenants_dispos ):
    """
    Génère les prompts system et user  nécessaire  pour la requete à l'IA
    """
    deadline_weeks = 4 # default value
    if mission.date_debut_projet and mission.date_fin_projet:
        delta = mission.date_fin_projet - mission.date_debut_projet
        deadline_weeks = max(1, int(delta.days / 7)) # max(1, ) pour éviter le "0 semaines si le projet est très court"
    
    mission_data = {
        "titre": mission.nom_projet, # Class Projets
        "competence_requise" : [competence.nom_competence for competence in mission.competences_requises], # on peut avoir plusieurs compétences requises
        "equipe_actuel_ids": [(i.id_intervenant,str(i.utilisateur.prenom_utilisateur) +" "+ str(i.utilisateur.nom_utilisateur)) for i in mission.intervenants],  # id de l'equipe actuel 
        "charge_estimee" : mission.charge_projet or 50, # heures par défaut
        "deadline_semaines" : deadline_weeks 
    }
    pool = [] # Liste de dictionnaire contenant les infos des intervenant dispos
    for intervenant in intervenants_dispos:
        
        skills_dict = {
            m.competence.nom_competence : m.niveau_maitrise
            for m in intervenant.maitrise_details
        }
        pool.append({
            "id": intervenant.id_intervenant,
            "nom": str(intervenant.utilisateur.prenom_utilisateur) +" "+ str(intervenant.utilisateur.nom_utilisateur),
            "skills": skills_dict,
            "dispo_h": intervenant.nb_heures_dispo or 0
        })


    prompt_system = """
    Tu es un algorithme expert d'affectation de ressources pour Telecom Nancy Services.
    Ton but est de composer l'équipe la plus performante possible (Elite Matching) et de répartir la charge de travail intelligemment.

    TES OBJECTIFS PAR ORDRE DE PRIORITÉ :
    1. **COUVERTURE & EXPERTISE (Priorité Absolue)** : Pour chaque compétence demandée par la mission, tu DOIS sélectionner l'intervenant disponible ayant le **niveau le plus élevé possible**.
    - Ne te contente pas d'un niveau moyen. Cherche l'excellence (le score le plus proche de 10).
    - Il n'y a pas de niveau minimum requis : prends simplement le meilleur profil disponible.

    2. **COMPLÉTION & COHÉRENCE** : Tu reçois une 'equipe_actuelle' (avec ses IDs). Ta suggestion finale DOIT inclure ces membres actuels + les nouveaux experts ajoutés.
    - INTERDICTION formelle de proposer un ID déjà présent dans l'équipe actuelle (pas de doublons).
    - Vise une équipe totale de 4 à 5 personnes maximum.

    3. **DISTRIBUTION DE LA CHARGE (CRITIQUE : HEBDOMADAIRE)** :
    Tu reçois une 'charge_estimee' (TOTAL d'heures du projet) et une 'deadline_semaines'.
    Tu dois d'abord calculer la **charge de travail par semaine** nécessaire (= charge_estimee / deadline_semaines).
    
    - Règle 1 : La somme des 'heures_attribuees' de tous les membres doit être égale à cette **charge par semaine** calculée (arrondie à l'entier supérieur).
    - Règle 2 : Les 'heures_attribuees' sont des **heures par semaine**. Ce chiffre doit être un ENTIER et ne doit JAMAIS dépasser les 'heures_dispo' de l'intervenant (qui sont aussi par semaine).
    - Règle 3 : Si un intervenant est très expert, essaie de maximiser ses heures hebdos dans la limite de sa disponibilité.

    FORMAT DE RÉPONSE :
    Réponds UNIQUEMENT par un JSON valide (sans texte avant/après) contenant une liste 'suggestions'.
    Chaque suggestion doit avoir :
    - 'score': note de 0 à 100 (basée sur la moyenne des compétences).
    - 'raison': explique les choix et précise le calcul hebdo (ex: "Besoin de 5h/semaine pour faire 50h en 10 semaines").
    - 'details_equipe': Une liste d'objets où chaque objet représente un membre (actuel ou nouveau) et contient :
        - 'id': ID de l'intervenant (entier)
        - 'nom': Nom de l'intervenant
        - 'heures_attribuees': Le nombre d'heures **par semaine** (int) que tu prélèves sur ses disponibilités.
    """

    prompt_user = f"""
    Voici la Mission : {json.dumps(mission_data)}

    Voici le Pool d'Intervenants Disponibles : {json.dumps(pool)}

    Trouve les 3 meilleures combinaisons. Réponds seulement par le JSON.
    """

    return prompt_system,prompt_user




# --- 3. APPEL API OPENROUTER ---
def call_ai_matching(prompt_system,prompt_user):
    url = "https://openrouter.ai/api/v1/chat/completions"
    key = os.getenv("API_KEY")
    api_model = os.getenv("API_MODEL")
     
    if not key: 
        print("Erreur:  API_KEY manquante dans le fichier .env")
        return None

    
    api_key = key
    payload = {
        "model": api_model,
        "messages": [
            {"role": "system", "content": prompt_system},
            {"role": "user", "content": prompt_user}
        ],
        "temperature": 0.2, # Faible -> déteministe
        
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:5000", # Requis par OpenRouter pour le classement gratuit
    }

    try:
        print("⏳ Envoi de la requête à l'IA...")
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        
        # Vérification des erreurs HTTP (401, 500, etc.)
        response.raise_for_status() 
        
        result = response.json()
        
        # Extraction du contenu du message
        content = result['choices'][0]['message']['content']
        
        # Nettoyage si l'IA bavarde avant le JSON (par sécurité)
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        data = json.loads(content)
        return data

    except requests.exceptions.HTTPError as err:
        print(f"❌ Erreur HTTP : {err}")
        print(f"Détail réponse : {response.text}") 
    except json.JSONDecodeError:
        print(f"❌ Erreur : L'IA n'a pas renvoyé un JSON valide.")
        print(f"Contenu reçu : {content}")
    except Exception as e:
        print(f"❌ Erreur inattendue : {e}")

# --- 4. EXÉCUTION ---
if __name__ == "__main__":
    resultats = call_ai_matching()
    
    if resultats:
        print("\n--- RÉSULTATS DU MATCHING ---")
        print(json.dumps(resultats, indent=2, ensure_ascii=False))

