# Guide d'Intégration - Données OWID COVID-19

## Télécharger les Données OWID

### Option 1: Via Git Clone (Complet - ~1GB)
```bash
git clone https://github.com/owid/covid-19-data.git owid_covid
cd owid_covid
ls public/data/

# Fichiers CSV disponibles:
# - owid-covid-data.csv (dataset complet - le plus volumineux)
# - owid-covid-data.json (même données en JSON)
```

### Option 2: Télécharger le Compact CSV (Recommandé - ~200MB)
```bash
wget https://catalog.ourworldindata.org/garden/covid/latest/compact/compact.csv
```

### Option 3: Via le Dataset Officiel OWID
```bash
# Accéder aux données via:
https://ourworldindata.org/coronavirus
# Télécharger "Full dataset (CSV)" depuis la page
```

---

## Structure du Dataset OWID Complet

Le fichier `owid-covid-data.csv` contient **50+ colonnes** pour tous les pays.

### Colonnes Principales:
```
iso_code, continent, location, date,
total_cases, new_cases, new_cases_smoothed,
total_deaths, new_deaths, new_deaths_smoothed,
total_tests, new_tests, tests_per_case, positive_rate,
total_vaccinations, people_vaccinated, people_fully_vaccinated, people_boosted,
total_boosters, ... (et d'autres métriques hospitalières)
```

---

## Préparer les Fichiers pour le Pipeline

### Étape 1: Télécharger les Données
```bash
# Depuis la racine du projet
mkdir -p data/bronze
cd data/bronze

# Télécharger le dataset complet
wget https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv

# Ou cloner et copier
git clone https://github.com/owid/covid-19-data.git temp_owid
cp temp_owid/public/data/owid-covid-data.csv .
rm -rf temp_owid
```

### Étape 2: Découper le Dataset en Fichiers Spécifiques

Créez ce script Python pour extraire les colonnes nécessaires:

```python
# scripts/prepare_owid_data.py
import pandas as pd

# Lire le dataset complet
df = pd.read_csv('data/bronze/owid-covid-data.csv')

# Fichier 1: Vaccination
vax_cols = ['iso_code', 'location', 'date', 'total_vaccinations', 
            'people_vaccinated', 'people_fully_vaccinated', 'people_boosted']
df_vax = df[vax_cols].dropna(subset=['location', 'date'])
df_vax.to_csv('data/bronze/vaccination.csv', index=False)
print(f"Saved {len(df_vax)} vaccination records")

# Fichier 2: Mortalité
mort_cols = ['iso_code', 'location', 'date', 'total_deaths', 'new_deaths']
df_mort = df[mort_cols].dropna(subset=['location', 'date'])
df_mort.to_csv('data/bronze/mortality.csv', index=False)
print(f"Saved {len(df_mort)} mortality records")

# Fichier 3: Tests
test_cols = ['iso_code', 'location', 'date', 'total_tests', 'new_tests', 
             'tests_per_case', 'positive_rate']
df_test = df[test_cols].dropna(subset=['location', 'date'])
df_test.to_csv('data/bronze/testing.csv', index=False)
print(f"Saved {len(df_test)} testing records")

# Fichier 4: Cas
cases_cols = ['iso_code', 'location', 'date', 'total_cases', 'new_cases']
df_cases = df[cases_cols].dropna(subset=['location', 'date'])
df_cases.to_csv('data/bronze/cases.csv', index=False)
print(f"Saved {len(df_cases)} cases records")
```

Exécuter:
```bash
python scripts/prepare_owid_data.py
```

### Étape 3: Uploader vers MinIO Bronze Bucket

```bash
# Via CLI ou Python

# Option 1: Uploader manuellement via interface MinIO
# http://localhost:9001 -> Bronze bucket

# Option 2: Via script Python
import boto3

s3_client = boto3.client(
    's3',
    endpoint_url='http://minio:9000',
    aws_access_key_id='minioadmin',
    aws_secret_access_key='minioadmin'
)

files = ['vaccination.csv', 'mortality.csv', 'testing.csv', 'cases.csv']
for file in files:
    s3_client.upload_file(
        f'data/bronze/{file}',
        'bronze',
        file
    )
    print(f"Uploaded {file}")
```

---

## Exécuter le Pipeline Complet

Une fois les fichiers dans le bucket Bronze:

```bash
# 1. S'assurer que MinIO et Spark sont actifs
docker compose up -d  # depuis le dossier docker/

# 2. Exécuter le pipeline
python scripts/run_pipeline.py

# Outputs:
# - process_data.py: Nettoie et valide → Silver layer
# - aggregate_data.py: Agrège et prépare → Gold layer
```

---

## Vérifier les Résultats

### Via PySpark
```python
spark = SparkSession.builder \
    .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
    .config("spark.hadoop.fs.s3a.access.key", "minioadmin") \
    .config("spark.hadoop.fs.s3a.secret.key", "minioadmin") \
    .getOrCreate()

# Vérifier Silver
df_silver = spark.read.parquet("s3a://silver/vaccination_cleaned/")
print(f"Silver records: {df_silver.count()}")
df_silver.show()

# Vérifier Gold
df_gold = spark.read.parquet("s3a://gold/vaccination_monthly/")
print(f"Gold records: {df_gold.count()}")
df_gold.show()
```

### Via MinIO Console
- Accédez à http://localhost:9001
- Naviguez dans les buckets: bronze, silver, gold
- Inspectez les fichiers

---

## Statistiques Attendues (Dataset Complet OWID)

### Bronze Layer
- vaccination.csv: ~200 millions de lignes
- mortality.csv: ~200 millions de lignes
- testing.csv: ~200 millions de lignes
- cases.csv: ~200 millions de lignes

### Silver Layer (Post-cleaning ~85% retention)
- vaccination_cleaned/: ~170 millions de lignes
- mortality_cleaned/: ~170 millions de lignes
- testing_cleaned/: ~170 millions de lignes
- cases_cleaned/: ~170 millions de lignes

### Gold Layer (Agrégé)
- vaccination_monthly/: ~6,000 records (pays × mois)
- vaccination_by_location/: ~195 records (pays)
- Similar pour mortality, testing, cases

---

## Optimisations pour Données Volumineuses

### 1. Partitionnement dans Silver
```python
# Dans process_data.py, remplacer:
# df_cleaned.write.mode("overwrite").parquet(silver_path)

# Par:
df_cleaned.write \
    .partitionBy("year", "month") \
    .mode("overwrite") \
    .parquet(silver_path)
```

### 2. Repartitionnage pour Agrégation
```python
# Dans aggregate_data.py:
df = helper_read_parquet(spark, silver_path)
df = df.repartition(50, "location", "year")  # Optimise joins
```

### 3. Caching Intermédiaire
```python
df.cache()
df.count()  # Force l'évaluation
```

---

## Filtrer par Pays (Exemple: Maroc)

Modifier `process_data.py` pour filtrer un pays spécifique:

```python
def process_bronze_to_silver_by_country(spark, env, country_name="Morocco"):
    # ... code existant ...
    
    for input_path, output_path, clean_func in file_mappings:
        df = helper_read_csv(spark, input_path)
        
        # Filtrer par pays
        df = df.filter(col("location") == country_name)
        
        # ... reste du nettoyage ...
```

Avantages:
- Données plus petites pour développement/test
- Temps d'exécution réduits
- Plus facile à valider

---

## Dépannage

### Erreur: "Missing column"
- Vérifier que les fichiers CSV contiennent les colonnes attendues
- Utiliser `helper_validate_required_columns()` pour identifier la colonne manquante

### Erreur: "File not found"
- Vérifier que les fichiers sont bien uploadés dans MinIO
- Vérifier le chemin s3a://

### Erreur: "Null pointer in aggregation"
- Cela ne devrait pas survenir grâce aux validations Silver
- Vérifier que le nettoyage Silver s'est exécuté correctement

### Performance Lente
- Réduire la partition temporairement pour test
- Utiliser partitionnement par année/mois
- Vérifier les ressources Spark (memory, cores)

---

## Prochaines Étapes d'Analyse

Après exécution réussie du pipeline, vous pouvez:

1. **Analyses Temporelles**: Trends vaccination, mortalité par mois
2. **Comparaisons Géographiques**: Taux par pays, par continent
3. **Corrélations**: Vaccination vs mortalité vs cas
4. **Machine Learning**: Prédiction de tendances
5. **Dashboards**: Visualisation avec Jupyter/Plotly

Tous les dados sont agrégés et prêts en Gold layer!
