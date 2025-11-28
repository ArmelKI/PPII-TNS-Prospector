CREATE TABLE roles (
    id_role SERIAL PRIMARY KEY, -- en postgre SERIAL signifie entier à 4 octets auto-incrémenté
    nom_role VARCHAR(100) NOT NULL
);