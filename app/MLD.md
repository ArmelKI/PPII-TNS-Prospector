roles(id_role, nom_role)
utilisateurs(id_utilisateur, prenom_utilisateur, nom_utilisateur, mail_utilisateur, mdp_utilisateur, #id_role)
intervenants(#id_intervenant, disponible, nb_heures_dispo)
intervenants[id_intervenant] => utilisateurs[id_utilisateur]
competences(id_competence, nom_competence)
intervenant_competence(#id_intervenant, #id_competence)
etats_relations(id_etat_relation, libelle_relation)
clients(id_client, raison_sociale, mail_client, telephone_client, secteur, date_dernier_contact, latitude, longitude)
interactions_client(id_interaction, #id_client, #id_etat_relation, date_interaction, detail_interaction)
conventions(id_convention, #id_client, type_convention, date_debut_convention, date_fin_convention, regles, cahier_charges, prix)
projets(id_projet, nom_projet, statut_projet, date_debut_projet, date_fin_projet, #id_convention)
intervenant_projet(#id_intervenant, #id_projet, date_debut_intervention, date_fin_intervention)
jalons(id_jalon, nom_jalon, statut_jalon, date_debut_jalon, date_fin_jalon, #id_projet)
taches(id_tache, nom_tache, description_tache, statut_tache, date_dernier_delai_tache, #id_jalon)
intervenant_tache(#id_intervenant, #id_tache)


