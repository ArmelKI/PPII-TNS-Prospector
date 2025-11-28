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