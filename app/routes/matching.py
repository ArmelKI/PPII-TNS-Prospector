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
    

# --- 1. LES DONNÉES (Générées précédemment) ---
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

# --- 2. TON ALGORITHME CORRIGÉ ---
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

# Première ébauche du programme mais il faut améliorer la pondération