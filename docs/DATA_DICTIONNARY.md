# Dictionnaire de Données - Prospector

Note : certaines valeurs de la colonne "Domaine" figurent entre crochets. 
Cela indique que l'attribut prend ses valeurs au sein d'un type de données prédéfini

Exemple : [StatutJalon] signifie que l'atribut prend ses valeurs parmi les valeurs énumérées au type "StatutJalon"

## Volet utilisateurs et rôles

### `roles`
**Description** : Référentiel des rôles et permissions des utilisateurs.

| Nom Physique | Type | Contraintes | Description | Domaine | Obligatoire |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id_role` | Integer | PK | Identifiant unique du rôle | | Oui |
| `nom_role` | String(100) | Not Null | Nom du rôle (Admin, Contributeur...) | | Oui |

### `utilisateurs`
**Description** : Membres de l'équipe (Utilisateurs du système).

| Nom Physique | Type | Contraintes | Description | Domaine | Obligatoire |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id_utilisateur` | Integer | PK | Identifiant unique | | Oui |
| `prenom_utilisateur` | String(100) | Not Null | Prénom de l'utilisateur | | Oui |
| `nom_utilisateur` | String(100) | Not Null | Nom de famille | | Oui |
| `mail_utilisateur` | String(150) | Unique, Not Null | Email servant d'identifiant | | Oui |
| `mdp_utilisateur` | String(255) | Not Null | Mot de passe haché (bcrypt) | | Oui |
| `id_role` | Integer | FK (roles.id_role) | Lien vers les permissions | | Oui |

---

## Volet intervenants et leurs compétences

### `intervenants`
**Description** : Profils techniques liés aux utilisateurs (Relation 1:1).

| Nom Physique | Type | Contraintes | Description | Domaine | Obligatoire |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id_intervenant` | Integer | PK, FK (utilisateurs, CASCADE) | Identifiant lié à l'User | | Oui |
| `disponible` | Boolean | Not Null, Default: True | Disponibilité de l'intervenant | True, False | Oui |
| `nb_heures_dispo` | Integer | | Heures de travail que l'intervenant peut accorder | | Non |
| `bulletin_adhesion` | String(255) | | Chemin vers le document | | Non |
| `carte_etudiante` | String(255) | | Chemin vers le document | | Non |
| `carte_vitale` | String(255) | | Chemin vers le document | | Non |
| `piece_identite` | String(255) | | Chemin vers le document | | Non |
| `photo_identite` | String(255) | | Chemin vers le document | | Non |
| `cv` | String(255) | | Chemin vers le document | | Non |

### `competences`
**Description** : Référentiel des compétences disponibles.

| Nom Physique | Type | Contraintes | Description | Domaine | Obligatoire |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id_competence` | Integer | PK | Identifiant unique | | Oui |
| `nom_competence` | String(150) | Not Null | Libellé de la compétence | | Oui |

### `intervenant_competence` (MaitriseCompetence)
**Description** : Niveau de maîtrise d'une compétence par un intervenant.

| Nom Physique | Type | Contraintes | Description | Domaine | Obligatoire |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id_intervenant` | Integer | PK, FK (intervenants, CASCADE) | ID de l'intervenant | | Oui |
| `id_competence` | Integer | PK, FK (competences, CASCADE) | ID de la compétence | | Oui |
| `niveau_maitrise` | Integer | Default: 0, Check(0-10) | Note de maîtrise | 0 à 10 | Oui |

---

## Volet clients
### `clients`
**Description** : Entreprises clientes ou prospects.

| Nom Physique | Type | Contraintes | Description | Domaine | Obligatoire |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id_client` | Integer | PK | Identifiant unique | | Oui |
| `raison_sociale` | String(200) | Not Null | Nom officiel de la société | | Oui |
| `mail_client` | String(150) | | Email de contact | | Non |
| `telephone_client` | String(30) | | Téléphone de contact | | Non |
| `secteur` | String(100) | | Branche d'activité | | Non |
| `date_dernier_contact` | Date | | Date de la dernière interaction | | Non |
| `latitude` | Numeric(10,7) | | Coordonnée GPS Nord | | Non |
| `longitude` | Numeric(10,7) | | Coordonnée GPS Est | | Non |

### `etats_relations`
**Description** : Libellés des types de relations clients.

| Nom Physique | Type | Contraintes | Description | Domaine | Obligatoire |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id_etat_relation` | Integer | PK | Identifiant unique | | Oui |
| `libelle_relation` | String(150) | Not Null | Nom de l'état (ex: Prospect) | | Oui |

### `interactions_client`
**Description** : Journal des échanges avec un client.

| Nom Physique | Type | Contraintes | Description | Domaine | Obligatoire |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id_interaction` | Integer | PK | Identifiant unique | | Oui |
| `id_client` | Integer | FK (clients, SET NULL) | Client concerné | | Oui |
| `date_interaction` | Date | Not Null | Date de l'interaction | | Oui |
| `detail_interaction` | Text | | Résumé de l'échange | | Non |
| `id_etat_relation` | Integer | FK (etats_relations, SET NULL)| État de la relation à ce moment | | Oui |

---

## Volet projets

### `conventions`
**Description** : Contrat au sein duquel un projet a lieu. 
Une convention de type "cadre" peut être rattachée à plusieurs projets, tandis qu'une convention de type "étude" n'est liée qu'à un seul projet. Voir l'attribut "type_convention".  
Pour simplifier le schéma, la cardinalité entre `conventions` et `projets` (qui varie selon le type de convention) est gérée **côté application**.

| Nom Physique | Type | Contraintes | Description | Domaine | Obligatoire |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id_convention` | Integer | PK | Identifiant unique | | Oui |
| `id_client` | Integer | FK (clients) | Client signataire | | Oui |
| `type_convention` | String(2) | Check('CE','CC') | Type de convention | CE, CC | Oui |
| `date_debut_convention`| Date | Not Null | Date de début | | Oui |
| `date_fin_convention` | Date | | Date de fin | | Non |
| `regles` | Text | | Règles contractuelles | | Non |
| `cahier_charges` | Text | | Description technique | | Non |
| `prix` | Numeric(10,2) | | Montant HT | | Non |

### `projets`
**Description** : Projets rattachés à une convention.

| Nom Physique | Type | Contraintes | Description | Domaine | Obligatoire |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id_projet` | Integer | PK | Identifiant unique | | Oui |
| `nom_projet` | String(200) | Not Null | Titre du projet | | Oui |
| `statut_projet` | Enum | Not Null, Def: PAS_COMMENCE | État actuel du projet | [StatutProjet] | Oui |
| `charge_projet` | Integer | Not Null, Def: 0 | Nombre total d'heures de travail requises pour mener à bien le projet | 0 à infini | Oui |
| `date_debut_projet` | Date | | Début effectif | | Non |
| `date_fin_projet` | Date | | Fin effective | | Non |
| `id_convention` | Integer | FK (conventions) | Convention parente | | Oui |
| `convention` | String(255) | | Chemin du fichier de convention | | Non |
| `bon_commande` | String(255) | | Chemin du fichier du bon de commande | | Non |
| `recap_mission` | String(255) | | Chemin du fichier du récapitulatif de mission | | Non |

### `jalons`
**Description** : Étapes (milestones) d'un projet.

| Nom Physique | Type | Contraintes | Description | Domaine | Obligatoire |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id_jalon` | Integer | PK | Identifiant unique | | Oui |
| `id_projet` | Integer | FK (projets, SET NULL) | Projet parent | | Oui |
| `nom_jalon` | String(200) | Not Null | Titre du jalon | | Oui |
| `statut_jalon` | Enum | Not Null, Def: A_VENIR | Statut temporel | [StatutJalon] | Oui |
| `date_debut_jalon` | Date | | Début prévu | | Non |
| `date_fin_jalon` | Date | | Fin prévue | | Non |

### `taches`
**Description** : Unités de travail assignables.

| Nom Physique | Type | Contraintes | Description | Domaine | Obligatoire |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id_tache` | Integer | PK | Identifiant unique | | Oui |
| `id_jalon` | Integer | FK (jalons, SET NULL) | Jalon parent | | Oui |
| `nom_tache` | String(200) | Not Null | Intitulé | | Oui |
| `description_tache` | Text | | Détails | | Non |
| `statut_tache` | Enum | Not Null, Def: PAS_COMMENCE | État d'avancement | [StatutTache] | Oui |
| `date_dernier_delai_tache` | Date | | Deadline | | Non |
| `id_intervenant_tache`| Integer | FK (intervenants, SET NULL) | Responsable assigné | | Non |

---

## Tables de liaison

### `intervenant_projet`
**Description** : Affectation des intervenants sur les projets.

| Nom Physique | Type | Contraintes | Description |
| :--- | :--- | :--- | :--- |
| `id_intervenant` | Integer | PK, FK (intervenants) | Intervenant concerné |
| `id_projet` | Integer | PK, FK (projets) | Projet concerné |
| `date_debut_intervention`| Date | | Début de l'affectation |
| `date_fin_intervention` | Date | | Fin de l'affectation |

### `intervenant_tache`
**Description** : Intervenant affecté à une tâche précise.

| Nom Physique | Type | Contraintes | Description |
| :--- | :--- | :--- | :--- |
| `id_intervenant` | Integer | PK, FK (intervenants) | Intervenant concerné |
| `id_tache` | Integer | PK, FK (taches) | Tâche concernée |

### `projet_competence`
**Description** : Compétences requises pour chaque projet.

| Nom Physique | Type | Contraintes | Description |
| :--- | :--- | :--- | :--- |
| `id_projet` | Integer | PK, FK (projets) | Projet concerné |
| `id_competence` | Integer | PK, FK (competences) | Compétence requise pour ce projet |