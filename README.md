# Prospector : application web d'aide à la prospection d'entreprises

Cette applicaiton web a pour objectif de faciliter la prospection de nouveaux clients pour Telecom Nancy Services.  
Prospector permet de gérer les clients de la junior, ses projets ainsi que les intervenants qui travaillent sur ces derniers.

L'application est conforme au RGPD : tout suppression des informations d'un client ou d'un utilisateur entraine la suppression complète de ses informations dans l'intégralité de l'application.

Vous trouverez un guide utilisateur à cette adresse [Nom du lien](./docs/Guid_utilisateur.md)

## Guide d'installation

### 1. Prérequis
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installé et **lancé**.
- Le port 5432 de votre machine est libre.

### 2. Configuration et Lancement
Ouvrez un terminal à la racine du projet :

```bash
cp ./app/.env.example ./app/.env

docker-compose --env-file ./app/.env up --build
# Cela peut prendre un peu de temps
```

### 3. L'application est maintenant lancée
Rendez-vous à l'adresse suivante : http://127.0.0.1:8000/auth/login?next=%2F