# Guide de Contribution

Bienvenue dans le projet **Covid-19 Data Analysis** ! Ce guide vous aidera à comprendre comment contribuer au projet, notamment en ajoutant de nouvelles transformations de données, et en respectant les conventions de style.

## Structure du Projet

Le projet suit une architecture modulaire propre (située dans le dossier `src/`) :
- **`src/common/`** : Contient la configuration globale (Spark, MinIO, variables d'environnement).
- **`src/ingestion/`** : Contient les scripts pour préparer et ingérer les données brutes dans la couche **Bronze**.
- **`src/transformation/`** : Contient la logique métier pour nettoyer les données (Bronze → Silver) et les agréger (Silver → Gold).
- **`src/pipeline/`** : Contient les orchestrateurs globaux (`run_pipeline.py`) et les scripts de validation.

Le projet est packagé avec un `setup.py`, ce qui permet de faire des imports absolus propres (e.g. `from src.common.utils import load_env`).

## Comment ajouter une nouvelle transformation ?

L'architecture suit le principe d'ouverture/fermeture (Open/Closed). Vous pouvez ajouter de nouvelles transformations sans modifier de manière destructive l'existant.

### 1. Ajout d'une transformation Bronze → Silver
1. Créez une nouvelle fonction de nettoyage dans `src/transformation/process_data.py`, par exemple `clean_new_data(df)`.
2. Dans la fonction `process_bronze_to_silver()`, ajoutez un nouveau tuple à la liste `file_mappings` :
   ```python
   (
       f"s3a://{bronze_bucket}/nouvelle_donnee.csv",
       f"s3a://{silver_bucket}/nouvelle_donnee_cleaned",
       clean_new_data
   )
   ```
3. Assurez-vous que votre fonction utilise les *helpers* existants (`helper_validate_required_columns`, etc.) pour maintenir la cohérence.

### 2. Ajout d'une transformation Silver → Gold
1. Créez une ou plusieurs fonctions d'agrégation dans `src/transformation/aggregate_data.py`, par exemple `aggregate_new_data_monthly(spark, env)`.
2. Appelez votre fonction dans la boucle d'exécution `process_silver_to_gold()`.

## Conventions de Code et Formatage

Pour garantir la lisibilité et la maintenabilité du code, nous utilisons les conventions suivantes :

1. **Formatage Automatique** : Le code doit être formaté en utilisant [Black](https://black.readthedocs.io/).
   ```bash
   black src/
   ```
2. **Linting** : Nous utilisons [Flake8](https://flake8.pycqa.org/) pour détecter les erreurs de syntaxe et les violations de style PEP-8.
   ```bash
   flake8 src/
   ```
3. **Docstrings** : Toutes les fonctions publiques doivent posséder des Docstrings explicites (idéalement au format Google ou Numpy) expliquant les paramètres d'entrée, le type de retour, et l'objectif de la fonction.
4. **Imports** : Utilisez uniquement des imports absolus (`from src...`). Ne faites jamais de `sys.path.append()`.

## Soumettre une Pull Request (PR)

1. Créez une branche à partir de `main` : `git checkout -b feature/ma-nouvelle-transformation`
2. Développez votre fonctionnalité et assurez-vous de bien formater votre code avec Black.
3. Lancez le script de validation pour vous assurer que l'architecture n'est pas brisée :
   ```bash
   python src/pipeline/validate_pipeline.py
   ```
4. Poussez vos modifications (`git push origin feature/ma-nouvelle-transformation`) et ouvrez une Pull Request sur le dépôt. Décrivez clairement ce que votre PR ajoute ou modifie.

*(Note : Les tests unitaires et l'intégration CI/CD ne sont pas encore configurés dans ce dépôt)*
