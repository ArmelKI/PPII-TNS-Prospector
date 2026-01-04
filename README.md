# Prospector : application web d'aide à la prospection d'entreprises

Cette applicaiton web a pour objectif de faciliter la prospection de nouveaux clients pour Telecom Nancy Services.  
Prospector permet de gérer les clients de la junior, ses projets ainsi que les intervenants qui travaillent sur ces derniers.

L'application est conforme au RGPD : tout suppression des informations d'un client ou d'un utilisateur entraine la suppression complète de ses informations dans l'intégralité de l'application.

Vous trouverez un guide utilisateur à cette adresse [ici](./docs/Guide_utilisateur.md)

## Guide d'installation

## Guide d'installation

### 1. Prérequis
- **Docker Engine** et le plugin **Docker Compose** sont installés sur votre machine.
- Le service Docker est démarré (ex: `sudo systemctl start docker`).
- Le port 5432 de votre machine est libre.

### 2. Configuration et Lancement
Ouvrez un terminal à la racine du projet :

```bash
# Copie des variables d'environnement
cp ./app/.env.example ./app/.env

# Lancement de l'application
# (Ajoutez 'sudo' devant la commande si votre utilisateur n'est pas dans le groupe docker)
docker compose --env-file ./app/.env up --build