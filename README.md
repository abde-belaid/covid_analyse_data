# Covid Data Analysis with Spark & MinIO

Ce projet est une structure d'initiation pour apprendre à développer une application de traitement de données avec Apache Spark et MinIO. Il fournit une base propre pour démarrer, avec des scripts Python, des notebooks Jupyter et une configuration Docker.

## Objectif

- Comprendre comment configurer un environnement de traitement de données local.
- Utiliser Spark pour charger, transformer et analyser des données.
- Utiliser MinIO comme stockage d'objets compatible S3.
- Disposer d'une architecture simple et évolutive pour un projet Big Data.

## Prérequis

- Python 3.11 ou plus récent
- Docker et Docker Compose installés
- Un terminal Linux ou macOS (ou WSL sous Windows)

## Mise en place

1. Copier le modèle d'environnement :
   ```bash
   cp .env-example .env
   ```

2. Créer un environnement virtuel Python :
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Mettre pip à jour et installer les dépendances :
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

## Lancer l'infrastructure Docker

Le projet contient une configuration Docker Compose pour démarrer Spark et MinIO.

```bash
cd docker
docker compose up -d
```

### Vérifier les services

- Spark Master UI : http://localhost:8080
- Spark Worker UI : http://localhost:8081
- MinIO Console : http://localhost:9001

## Utilisation

### Exécuter le script principal

Ce script lance une session Spark et exécute un exemple d'ingestion et de traitement.

```bash
python scripts/main.py
```

### Explorer avec Jupyter

Ouvrez le notebook de démarrage :

```bash
jupyter lab
```

Puis ouvrez `notebooks/00-data-exploration.ipynb`.

## Structure du projet

- `scripts/` : code Python principal
  - `main.py` : point d'entrée pour exécuter le pipeline
  - `ingest_data.py` : fonction d'ingestion des données
  - `process_data.py` : logique de traitement
  - `utils.py` : fonctions utilitaires et chargement des variables d'environnement
- `notebooks/` : notebooks Jupyter pour l'exploration
- `docker/` : configuration Docker Compose et conteneurs
- `requirements.txt` : dépendances Python
- `.env-example` : modèle de configuration
- `.gitignore` : fichiers à ignorer dans Git

## Bonnes pratiques

- Ne versionnez jamais votre environnement virtuel (`.venv`) ou les données volumineuses.
- Utilisez `.env` pour les paramètres locaux et ne le partagez pas.
- Ajoutez des tests et des scripts de validation dès que possible.
- Documentez chaque étape de votre pipeline pour faciliter la maintenance.

## Notes

- Le service applicatif Docker n'est pas encore développé : le projet est actuellement conçu pour un développement local.
- Vous pouvez compléter `scripts/ingest_data.py` pour lire réellement depuis MinIO avec `spark.read.csv()` ou `spark.read.format("csv")`.
- Le notebook `notebooks/00-data-exploration.ipynb` est le meilleur point de départ pour analyser vos données.

## Arrêter les services

```bash
cd docker
docker compose down
```
