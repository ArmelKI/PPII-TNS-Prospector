CREATE TYPE statut_projet_enum AS ENUM (
    'Pas commencé', 'En cours', 'Terminé', 'Bloqué', 'Stand-By'
);

CREATE TYPE statut_jalon_enum AS ENUM (
    'À venir', 'Actuel', 'Passé'
);

CREATE TYPE statut_tache_enum AS ENUM (
    'Pas commencé', 'En cours', 'Terminé', 'Bloqué', 'Stand-By'
);

CREATE TABLE roles (
    id_role SERIAL PRIMARY KEY, -- en postgre SERIAL signifie entier à 4 octets auto-incrémenté
    nom_role VARCHAR(100) NOT NULL
);

CREATE TABLE utilisateurs (
    id_utilisateur SERIAL PRIMARY KEY,
    prenom_utilisateur VARCHAR(100) NOT NULL,
    nom_utilisateur VARCHAR(100) NOT NULL,
    mail_utilisateur VARCHAR(150) UNIQUE NOT NULL,
    mdp_utilisateur VARCHAR(255) NOT NULL,
    id_role INT NOT NULL,
    FOREIGN KEY (id_role) REFERENCES roles(id_role)
);

CREATE TABLE intervenants (
    id_intervenant INT PRIMARY KEY,
    disponible BOOLEAN NOT NULL DEFAULT TRUE,
    nb_heures_dispo INT,
    bulletin_adhesion VARCHAR(255),
    carte_etudiante VARCHAR(255),
    carte_vitale VARCHAR(255),
    piece_identite VARCHAR(255),
    photo_identite VARCHAR(255),
    cv VARCHAR(255),
    FOREIGN KEY (id_intervenant) REFERENCES utilisateurs(id_utilisateur)
);

CREATE TABLE competences (
    id_competence SERIAL PRIMARY KEY,
    nom_competence VARCHAR(150) NOT NULL
);

CREATE TABLE intervenant_competence (
    id_intervenant INT,
    id_competence INT,
    niveau_maitrise INT CONSTRAINT range_check CHECK (niveau_maitrise BETWEEN 0 AND 10)
    PRIMARY KEY (id_intervenant, id_competence),
    FOREIGN KEY (id_intervenant) REFERENCES intervenants(id_intervenant),
    FOREIGN KEY (id_competence) REFERENCES competences(id_competence)
);

CREATE TABLE etats_relations (
    id_etat_relation SERIAL PRIMARY KEY,
    libelle_relation VARCHAR(150) NOT NULL
);

CREATE TABLE clients (
    id_client SERIAL PRIMARY KEY,
    raison_sociale VARCHAR(200) NOT NULL,
    mail_client VARCHAR(150),
    telephone_client VARCHAR(30),
    secteur VARCHAR(100),
    date_dernier_contact DATE,
    latitude DECIMAL(10, 7),
    longitude DECIMAL(10, 7)
);

CREATE TABLE interactions_client (
    id_interaction SERIAL PRIMARY KEY,
    id_client INT NOT NULL,
    id_etat_relation INT NOT NULL,
    date_interaction DATE NOT NULL,
    detail_interaction TEXT,
    FOREIGN KEY (id_client) REFERENCES clients(id_client),
    FOREIGN KEY (id_etat_relation) REFERENCES etats_relations(id_etat_relation)
);

CREATE TABLE conventions (
    id_convention SERIAL PRIMARY KEY,
    id_client INT NOT NULL,
    type_convention VARCHAR(2) NOT NULL CHECK (type_convention IN ('CE','CC')),
    date_debut_convention DATE NOT NULL,
    date_fin_convention DATE,
    regles TEXT,
    cahier_charges TEXT,
    prix DECIMAL(10, 2),
    FOREIGN KEY (id_client) REFERENCES clients(id_client)
);

CREATE TABLE projets (
    id_projet SERIAL PRIMARY KEY,
    nom_projet VARCHAR(200) NOT NULL,
    statut_projet statut_projet_enum NOT NULL DEFAULT 'Pas commencé',
    date_debut_projet DATE,
    date_fin_projet DATE,
    id_convention INT NOT NULL, -- il faudra vérifier côté application qu'une CE ne peut avoir qu'un seul projet
    FOREIGN KEY (id_convention) REFERENCES conventions(id_convention)
);

CREATE TABLE intervenant_projet (
    id_intervenant INT,
    id_projet INT,
    date_debut_intervention DATE,
    date_fin_intervention DATE,
    PRIMARY KEY (id_intervenant, id_projet),
    FOREIGN KEY (id_intervenant) REFERENCES intervenants(id_intervenant),
    FOREIGN KEY (id_projet) REFERENCES projets(id_projet)
);

CREATE TABLE jalons (
    id_jalon SERIAL PRIMARY KEY,
    nom_jalon VARCHAR(200) NOT NULL,
    statut_jalon statut_jalon_enum NOT NULL DEFAULT 'À venir',
    date_debut_jalon DATE,
    date_fin_jalon DATE,
    id_projet INT NOT NULL,
    FOREIGN KEY (id_projet) REFERENCES projets(id_projet)
);

CREATE TABLE taches (
    id_tache SERIAL PRIMARY KEY,
    nom_tache VARCHAR(200) NOT NULL,
    description_tache TEXT,
    statut_tache statut_tache_enum  NOT NULL DEFAULT 'Pas commencé',
    date_dernier_delai_tache DATE,
    id_jalon INT NOT NULL,
    FOREIGN KEY (id_jalon) REFERENCES jalons(id_jalon)
);

CREATE TABLE intervenant_tache (
    id_intervenant INT,
    id_tache INT,
    PRIMARY KEY (id_intervenant, id_tache),
    FOREIGN KEY (id_intervenant) REFERENCES intervenants(id_intervenant),
    FOREIGN KEY (id_tache) REFERENCES taches(id_tache)
);