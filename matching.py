
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



def create_ai_prompt(mission,intervenants_dispos ):
    """
    Missions = Projets 
    mission est un élément de Projets
    {% for mission in Projets %}
        create_ai_prompt(mission,intervenants_dispots )
    {% endfor %}

    intervenants_dispos = Intervenant.query.filter(Intervenants.disponible == True).all()

    """
    

    
    mission_data = {
        "titre": mission.nom_projet, # Class Projets
        "competence_requise" : "java", # on peut avoir plusieurs compétences requises 
        "charge_estimée" : 15, # heures par défaut
        "deadline_semaines" : 10 #
    }
    pool = [] # Liste de dictionnaire contenant les infos des intervenant dispos
    for intervenant in intervenants_dispos:
        # On construit le dict des compétences de l'intervenant
        #  skills = {c.nom_competence: intervnant_competence.id_intervenant for c in i.competences} # Inaccessible tant que la db n'est pas modifié
        pool.append({
            "id": intervenant.id_intervenant,
            "nom": str(intervenant),
            "skills": "skills",
            "dispo_h": intervenant.nb_heures_dispo or 0
        })


    prompt_system = """
    Tu es un algorithme expert d'affectation de ressources pour Telecom Nancy Services.
    Tes objectifs sont :
    1. Trouver la meilleure équipe d'intervenants pour la mission donnée[cite: 3].
    2. Assurer que TOUTES les compétences requises sont couvertes (niveau maximal prioriser).
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

    return prompt_system,prompt_user


    

        
     
        

    

# --- 1. DONNÉES À ENVOYER (JSON) ---
# Dans ton app Flask, ces données viendront de tes objets SQLAlchemy convertis en dict
mission_data = {
    "titre": "Plateforme SaaS Complète",
    "competences_requises": ["Python", "React", "Docker"],
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
Ton but est de composer l'équipe la plus performante possible (Elite Matching).

TES OBJECTIFS PAR ORDRE DE PRIORITÉ :
1. **COUVERTURE & EXPERTISE (Priorité Absolue)** : Pour chaque compétence demandée par la mission, tu DOIS sélectionner l'intervenant disponible ayant le **niveau le plus élevé possible**.
   - Ne te contente pas d'un niveau moyen. Cherche l'excellence (le score le plus proche de 10).
   - Il n'y a pas de niveau minimum requis : prends simplement le meilleur profil disponible.

2. **MINIMISATION DE L'ÉQUIPE** : Si un seul intervenant est expert dans toutes les compétences, choisis-le (Solo). Sinon, combine les experts (Duo/Trio) pour couvrir tous les besoins au meilleur niveau.

3. **FAISABILITÉ** : Vérifie que la somme des disponibilités (heures/semaine) de l'équipe est cohérente avec la charge de travail.

FORMAT DE RÉPONSE :
Réponds UNIQUEMENT par un JSON valide (sans texte avant/après) contenant une liste 'suggestions'.
Chaque suggestion doit avoir :
- 'equipe': liste des noms
- 'score': note de 0 à 100 (basée sur la moyenne des compétences des intervenants choisis pour la mission)
- 'raison': explique pourquoi ces experts ont été choisis (ex: "Alice est la meilleure en Python (9/10)").
"""
prompt_user = f"""
Voici la Mission : {json.dumps(mission_data)}

Voici le Pool d'Intervenants Disponibles : {json.dumps(pool_intervenants)}

Trouve les 3 meilleures combinaisons. Réponds seulement par le JSON.
"""



# --- 3. APPEL API OPENROUTER ---
def call_ai_matching():
    url = "https://openrouter.ai/api/v1/chat/completions"
    key = os.getenv("API_KEY")
    api_model = os.getenv("API_MODEL")
     
    if not api_key: 
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
Il faudra modifier la DB en conséquence pour qu'il y'ait un dicitionaire clé/compétence requise  valeur/score de la compétence
De meme il faut pour chaque compétence de l'intervenant qu'il y'ait un score associer (sinon par défaut on le met a 0/10)

"""