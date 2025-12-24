# PPII - Gestion des Intervenants 🐐

Projet de gestion des intervenants et clients développé dans le cadre du PPII (S5).

## Lancement Rapide avec Docker (Recommandé)

Cette méthode est la plus simple car elle configure automatiquement l'application et la base de données PostgreSQL.

### 1. Prérequis
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installé et **lancé**.

### 2. Configuration et Lancement
Ouvrez un terminal à la racine du projet :

```bash
# 1. Créer le fichier d'environnement pour l'application
cp .env.example ./app/.env

# 2. Construire et lancer les conteneurs
docker-compose --env-file ./app/.env up --build