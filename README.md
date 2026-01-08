# Prospector : application web d'aide à la prospection d'entreprises

Cette applicaiton web a pour objectif de faciliter la prospection de nouveaux clients pour Telecom Nancy Services.  
Prospector permet de gérer les clients de la junior, ses projets ainsi que les intervenants qui travaillent sur ces derniers.

L'application est conforme au RGPD : toute suppression des informations d'un client ou d'un utilisateur entraine la suppression complète de ses informations dans l'intégralité de l'application.

Vous trouverez un guide utilisateur à cette [adresse](./docs/Guide_utilisateur.md).

## Guide d'installation

### 1. Prérequis
- **Docker Engine** et le plugin **Docker Compose** sont installés sur votre machine.
- Le service Docker est démarré (ex: `sudo systemctl start docker`).
- Le port 5432 de votre machine est libre.

### 2. Configuration et Lancement
Ouvrez un terminal à la racine du projet.
Copiez-y successivement les commandes suivantes :

```bash
cp ./app/.env.example ./app/.env

docker compose --env-file ./app/.env up --build

# Seulement pour avoir des données de test !
python3 seed.py

```

Si il semble que la DB n'a pas été correctement créée, lancez la commande suivante pendant que le conteneur est lancé  :
```bash
python3 init_db.py
```

Ouvrez maintenant http://127.0.0.1:8000, enjoy!

**Rendez-vous [ici](./docs/Guide_utilisateur.md) pour le manuel utilisateur.**

## Cas particuluer : Docker ne fonctionne pas, ou une affiche une erreur d'authetification

Lorsque Docker ne fonctionne pas, voici comment lancer l'application avec Python.

**Pré-requis** : 
- Python 3 est installé
- PostGreSQL installé

Lancez successivement les commandes suivantes

```bash
cp ./app/.env.example ./app/.env

python3 -m venv .venv

source ./.venv/bin/activate

pip install --no-cache-dir -r requirements.txt

createdb prospector

# uniquement au premier lancer !
python3 seed.py # initialise avec des données de test
# ou
python3 init_db.py #initialise sans données de test

python3 app.py
```

Ouvrez maintenant http://127.0.0.1:8000, enjoy!
