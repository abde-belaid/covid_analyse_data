# Guide Pas à Pas : Analyse de Données Covid-19 (Maroc) avec Spark et MinIO

Ce document détaille chaque étape du projet, de l'architecture aux scripts Python, pour vous aider à comprendre comment la solution complète a été développée et comment l'utiliser.

## 1. Architecture du Projet (Médaillon)

Le projet implémente l'architecture "Médaillon", très populaire en Big Data, pour organiser le cycle de vie de la donnée :
- **Bronze (Brut)** : Données telles qu'elles ont été ingérées, sans modification (ici, le fichier CSV des vaccinations au Maroc issu de *Our World in Data*).
- **Silver (Nettoyé)** : Données dont les valeurs nulles ont été gérées, les types corrigés, et stockées au format optimisé (Parquet).
- **Gold (Agrégé)** : Données prêtes pour l'analyse métier (ici, une agrégation mensuelle pour connaître le nombre maximum de personnes vaccinées par mois).

Ces différentes couches de données sont stockées dans des *Buckets* sur un serveur **MinIO** local. Le traitement entre chaque couche est assuré par **Apache Spark** (PySpark).

## 2. Infrastructure (Docker)

L'infrastructure repose sur 3 conteneurs définis dans le fichier `docker/docker-compose.yml` :
1. **MinIO** : Le stockage objet (équivalent local de AWS S3). Il est accessible sur `http://localhost:9001` (interface web) et `http://localhost:9000` (API pour Spark/Python).
2. **Spark Master** : Le nœud maître gérant le cluster Spark (`http://localhost:8080`).
3. **Spark Worker** : Un nœud de calcul exécutant les tâches de traitement.

### Pour démarrer l'infrastructure :
```bash
cd docker
docker compose up -d
```
> Attendez quelques secondes pour que les services démarrent complètement.

## 3. Les Scripts Python

Les scripts se trouvent dans le dossier `scripts/` et ont chacun un rôle précis :

### `scripts/utils.py`
Charge les variables d'environnement depuis le fichier `.env` pour éviter d'écrire en dur les mots de passe et adresses dans le code.

### `scripts/minio/minio_utils.py`
Contient la fonction `create_buckets()` qui se connecte à MinIO (via la librairie Python `minio`) et s'assure que les 3 buckets (`bronze`, `silver`, `gold`) existent bien.

### `scripts/spark/spark_config.py`
Configure la session Apache Spark pour qu'elle puisse communiquer avec MinIO. 
> [!NOTE]
> Nous avons ajouté `.config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.3.2,...")` pour que Spark télécharge automatiquement les librairies nécessaires à la communication S3.

### `scripts/ingest_data.py`
Se charge de la couche **Bronze** :
1. Télécharge le fichier CSV des données de vaccination du Maroc depuis le dépôt Github de *Our World In Data*.
2. Utilise le client MinIO pour envoyer directement ces données brutes dans le bucket `bronze` sous le nom `covid_data_morocco.csv`.

### `scripts/process_data.py`
Se charge des couches **Silver** et **Gold** via Apache Spark :
1. **`process_bronze_to_silver`** : Lit le CSV depuis le bucket `bronze`, supprime les lignes sans date, remplace les valeurs nulles par des zéros, puis sauvegarde le résultat au format **Parquet** (plus rapide et compressé) dans le bucket `silver`.
2. **`process_silver_to_gold`** : Lit les données Parquet depuis `silver`, convertit la date, regroupe les données par année et par mois pour calculer le nombre maximum de personnes totalement vaccinées (`max_fully_vaccinated`), puis sauvegarde ce résultat final dans le bucket `gold`.

### `scripts/main.py`
C'est le chef d'orchestre. Il exécute les étapes séquentiellement :
1. Création des buckets.
2. Ingestion des données.
3. Traitement avec Spark.

## 4. Exécuter le Projet

Une fois l'environnement virtuel activé (`source .venv/bin/activate`), que les dépendances sont installées (`pip install -r requirements.txt`), et que les conteneurs Docker tournent, lancez la commande suivante depuis la racine du projet :

```bash
python scripts/main.py
```

Vous devriez voir les logs Spark s'afficher, ainsi que les confirmations d'écriture dans les buckets MinIO.

## 5. Bonnes Pratiques Appliquées
- **Modularité** : Le code est découpé par responsabilité (ingestion vs traitement).
- **Sécurité** : Utilisation d'un `.env` pour cacher les identifiants MinIO.
- **Optimisation** : Utilisation du format Parquet pour les couches Silver et Gold, car il est adapté au Big Data.
- **Reproductibilité** : Le téléchargement du jeu de données est automatisé, nul besoin de télécharger un fichier manuellement.
