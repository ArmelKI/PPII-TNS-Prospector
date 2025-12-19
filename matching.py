"""
def gale_shapley(men_preferences, women_preferences):
    n = len(men_preferences)
    free_men = list(men_preferences.keys())  # All men start out free
    engaged_pairs = {}  # To store engaged pairs
    men_proposals = {man: [] for man in men_preferences}  # Track proposals

    # While there are free men who haven't proposed to all women
    while free_men:
        man = free_men[0]  # Grab the first free man
        man_pref = men_preferences[man]
        for woman in man_pref:
            if woman not in men_proposals[man]:
                men_proposals[man].append(woman)  # Record the proposal

                # If the woman is free, engage them
                if woman not in engaged_pairs.values():
                    engaged_pairs[man] = woman
                    free_men.remove(man)
                    break
                else:
                    # If the woman is already engaged, check if she prefers the new man
                    current_man = next(m for m, w in engaged_pairs.items() if w == woman)
                    woman_pref = women_preferences[woman]
                    if woman_pref.index(man) < woman_pref.index(current_man):
                        # Engage the new man and free the current one
                        engaged_pairs[man] = woman
                        free_men.remove(man)
                        free_men.append(current_man)
                        del engaged_pairs[current_man]
                        break

    return engaged_pairs

# Example usage
men_preferences = {
    'Man1': ['Woman1', 'Woman2', 'Woman3'],
    'Man2': ['Woman2', 'Woman3', 'Woman1'],
    'Man3': ['Woman3', 'Woman1', 'Woman2'],
}

women_preferences = {
    'Woman1': ['Man2', 'Man1', 'Man3'],
    'Woman2': ['Man1', 'Man2', 'Man3'],
    'Woman3': ['Man3', 'Man1', 'Man2'],
}

result = gale_shapley(men_preferences, women_preferences)
print(result) 

def ponderate(intervenant,ponderation) :# donne la pondération  d'un intervenant par un projet 
    return {key:ponderation[val] for key,val in intervenant.items() if val in ponderation}
    # finaalement la ponderationd est effectivemnt à sens unique en fonction de la préférence du projet et l'avis d'un intervenant ne compte pas vraiement pour le moment
    

# -- DONNES TEST --- 
intervenants = [
    {"id": 1, "nom": "Alice", "metier": "Data Scientist", "techno": "Python", "niveau": "Senior", "ville": "Paris", "dispo": "Immédiate"},
    {"id": 2, "nom": "Bob", "metier": "Dev Backend", "techno": "Java", "niveau": "Junior", "ville": "Lyon", "dispo": "3 mois"},
    {"id": 3, "nom": "Charlie", "metier": "Dev Frontend", "techno": "React", "niveau": "Confirmé", "ville": "Télétravail", "dispo": "Immédiate"},
    {"id": 4, "nom": "David", "metier": "Dev Fullstack", "techno": "JavaScript", "niveau": "Junior", "ville": "Paris", "dispo": "2 semaines"}
]

projets_preferences = {
    "Projet IA": {"Python": 20, "Data Scientist": 15, "Senior": 10, "Paris": 5, "Immédiate": 5},
    "Projet Web": {"React": 20, "Télétravail": 15, "JavaScript": 15, "Junior": 2, "AWS": 30}
}

def matching(projets: dict, intervenants: list):
    projets_preferences_result = {}
    for projet_nom, ponderation in projets.items():
        intervenantsScore = []
        
        for intervenant in intervenants:
            score_brut = 0
            valeurs_intervenant = list(intervenant.values())
            
            # On calcule le score total
            for valeur in valeurs_intervenant:
                if valeur in ponderation:
                    score_brut += ponderation[valeur]
            
            # On fait la moyenne pour obtenir le score 
            n = len(valeurs_intervenant) 
            if n > 0:
                score_final = (1/n) * score_brut
            else:
                score_final = 0
            intervenantsScore.append((intervenant, score_final))
        intervenantsScore.sort(key=lambda x: x[1], reverse=True)
        projets_preferences_result[projet_nom] = intervenantsScore
        
    return projets_preferences_result

# --- 3. TEST ---
resultats = matching(projets_preferences, intervenants)

# Affichage propre des résultats
for projet, liste_candidats in resultats.items():
    print(f"\n--- Résultat pour : {projet} ---")
    for candidat in liste_candidats:
        nom = candidat[0]['nom']
        score = round(candidat[1], 2) # Arrondi pour la lisibilité
        print(f"Intervenant : {nom} | Score : {score}")






    # Algo de matching (gale Shapley modifié): 
    # Finalement il faudrait plutot que pour chaque projet il y ai ses intervenants préférés et de meme une préférence d'un projet  pour un intervenant particulié pour avoir un tableau à double enrée 
   
    # Maintenant le problème de la pondération est quelle est a sens unique et que elle ne permettrait que de classer les intervenants entre eux et non de définir un odre de préférence par rapport aux projets 
    # On est quand meme dans une situtation qui pourrait etre résolu par un gale shapley car on a n intervenant pour n projet et un intervenant par projet.
    # Ce qu'il retournera sera un tableau avec une solution de stable matching 
    # L'ordre de préférence qui définira les suggestions d'intervenant dans l'ordre décroissant de préférence  sera à renvoyer  avant pour effectuer la liste de suggestion ( plutot qu'un reel matching)


    # On peut résoudre ce problème en attribuant à chaque projet sa propre pondération, puis à crée une pondération. 



print(matching(projets_preferences,intervenants))
"""
# Première ébauche du programme mais il faut améliorer la pondération

########## INTERFACE CALL API IA ####################

# Selon leur programme de con il faudrait faire des call a une ia pour trouver la solution de mattching *sigh* 



"""
import requests
import json
response = requests.post(
  url="https://openrouter.ai/api/v1/chat/completions",
  headers={
    "Authorization": "Bearer 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",
  },
  data=json.dumps({
    "model": "mistralai/devstral-2512:free",
    "messages": [
      {
        "role": "user",
        "content": "Qu'est ce que Telecom Nancy?"
      }
    ],
    # "temperature": 0.7, # Ajuster la créativité de la réponse
    # "max_tokens": 512,  # Limite le nombre de tokens dans la réponse
  })
)
print(response.json())
"""
# Cependant si on devait faire appel a l'ia pour résoudre ce problème de matching à chaque fois qu'on ajoutait un nouvelle intervenant ou un nouveau projet le temps d'actualisation serait interminable. 
# Mieux vaut se baser sur un  algorithme pur et dur avec pondération plus complexe.

from dotenv import load_dotenv
import os
import requests
import json


load_dotenv()
# --- 1. DONNÉES À ENVOYER (JSON) ---
# Dans ton app Flask, ces données viendront de tes objets SQLAlchemy convertis en dict
mission_data = {
    "titre": "Plateforme SaaS Complète",
    "competences_requises": {"Python": 6, "React": 6, "Docker": 5},
    "charge_estimee": 150,
    "deadline_semaines": 10
}

pool_intervenants = [
    {"id": 1, "nom": "Alice", "skills": {"Python": 9, "Django": 8}, "dispo_h": 5},
    {"id": 2, "nom": "Bob", "skills": {"React": 8, "JS": 8}, "dispo_h": 15},
    {"id": 3, "nom": "Charlie", "skills": {"Python": 7, "SQL": 8}, "dispo_h": 25},
    {"id": 4, "nom": "David", "skills": {"Docker": 8, "AWS": 7, "Python": 5}, "dispo_h": 10}
]

# --- 2. CONSTRUCTION DU PROMPT ---
# On injecte les règles métier directement dans le prompt
prompt_system = """
Tu es un algorithme expert d'affectation de ressources pour Telecom Nancy Services.
Tes objectifs sont :
1. Trouver la meilleure équipe d'intervenants pour la mission donnée[cite: 3].
2. Assurer que TOUTES les compétences requises sont couvertes (niveau max de l'équipe >= niveau requis).
3. Minimiser le nombre d'intervenants (1 personne est mieux que 2).
4. Vérifier que la disponibilité totale est suffisante.

Format de réponse attendu : Uniquement un JSON valide contenant une liste 'suggestions'.
Chaque suggestion doit avoir : 'equipe' (liste des noms), 'score' (0-100), et 'raison'.
"""

prompt_user = f"""
Voici la Mission : {json.dumps(mission_data)}

Voici le Pool d'Intervenants Disponibles : {json.dumps(pool_intervenants)}

Trouve les 3 meilleures combinaisons. Réponds seulement par le JSON.
"""

# --- 3. APPEL API OPENROUTER ---
def call_ai_matching():
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    # Remplace par ta vraie clé API (celle dans ton code précédent semblait être une clé de test ou expirée)
    api_key = "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"
    payload = {
        "model": "mistralai/devstral-2512:free",
        "messages": [
            {"role": "system", "content": prompt_system},
            {"role": "user", "content": prompt_user}
        ],
        "temperature": 0.2, # Faible pour être logique et déterministe
        # "response_format": { "type": "json_object" } # Utile si le modèle le supporte
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
        print(f"Détail réponse : {response.text}") # Très important pour le debug
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


"""
CHOSE A CORRIGER DANS LE FONCTIONNEMENT ACTUEL DU SITE

L'export csv ne redonne que le fichier contenant les  intervenants ce qui n'a pas l'air d'etre demandé et n'a pas trop de sens 
Ajouter la possibilité d'un import d'un fichier csv qui ajoute des clients. Pour le moement on a pas cette fonctionalité  

Il faut aussi une page historique des missions (semble être les taches dans la DB) + export des données en csv et import ( pas trop de sens de devoir faire un import mais bon)


Rendre cette notion de mission clair + il faut que je vois le lien avec les projets dans le MCD

Il semble que ces taches sont dans des jalons qui sont eux dans des projets  respectifs 



"""


