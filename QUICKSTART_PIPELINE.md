# Quickstart - Pipeline de Preprocessing COVID-19

## Démarrage Rapide en 5 Étapes

### Étape 1: Télécharger les Données OWID COVID-19

```bash
# Créer le répertoire bronze
mkdir -p data/bronze
cd data/bronze

# Télécharger le dataset complet OWID (~500MB)
wget https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv

# Ou pour test rapide (Maroc seulement, filtré après)
cd ../..
```

**Options alternative** (si wget ne fonctionne pas):
```bash
# Via curl
curl -O https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv

# Via git
git clone https://github.com/owid/covid-19-data.git
cp owid-covid-19-data/public/data/owid-covid-data.csv data/bronze/
```

### Étape 2: Préparer et Diviser les Données par Type

```bash
# Extraire les données par type (vaccination, mortality, testing, cases)
python scripts/prepare_owid_data.py \
    --input data/bronze/owid-covid-data.csv \
    --output data/bronze

# Cela génère:
# - data/bronze/vaccination.csv
# - data/bronze/mortality.csv
# - data/bronze/testing.csv
# - data/bronze/cases.csv
```

**Pour test avec un seul pays**:
```bash
python scripts/prepare_owid_data.py \
    --input data/bronze/owid-covid-data.csv \
    --output data/bronze \
    --country "Morocco"
```

### Étape 3: Uploader vers MinIO (Bronze Bucket)

Accédez à l'interface MinIO:
```
http://localhost:9001
Credentials: minioadmin / minioadmin
```

Créez le bucket "bronze" s'il n'existe pas, puis uploadez les 4 fichiers CSV.

**Alternative CLI**:
```python
# scripts/upload_to_minio.py (crée si nécessaire)
import boto3

s3 = boto3.client('s3', 
    endpoint_url='http://minio:9000',
    aws_access_key_id='minioadmin',
    aws_secret_access_key='minioadmin'
)

# Uploader les fichiers
for file in ['vaccination.csv', 'mortality.csv', 'testing.csv', 'cases.csv']:
    s3.upload_file(f'data/bronze/{file}', 'bronze', file)
```

### Étape 4: Exécuter le Pipeline Complet

```bash
# S'assurer que Spark et MinIO sont actifs
docker compose up -d  # depuis le dossier docker/

# Exécuter le pipeline complet: Bronze → Silver → Gold
python scripts/run_pipeline.py
```

**Exécution par étapes** (si vous préférez):
```bash
# Étape 1: Nettoyage (Bronze → Silver)
python scripts/process_data.py

# Étape 2: Agrégation (Silver → Gold)
python scripts/aggregate_data.py
```

### Étape 5: Analyser les Données

```bash
# Exécuter les exemples d'analyse
python scripts/analysis_examples.py

# Ou explorer avec PySpark
python
>>> from pyspark.sql import SparkSession
>>> spark = SparkSession.builder.appName("Explore").getOrCreate()
>>> vax = spark.read.parquet("s3a://gold/vaccination_monthly/")
>>> vax.count()
>>> vax.show()
>>> spark.stop()
```

---

## Structure des Répertoires

```
covid_data_analysis/
├── data/
│   └── bronze/                          # Données brutes OWID
│       ├── vaccination.csv
│       ├── mortality.csv
│       ├── testing.csv
│       └── cases.csv
│
├── scripts/
│   ├── process_data.py                  # Bronze → Silver
│   ├── aggregate_data.py                # Silver → Gold
│   ├── run_pipeline.py                  # Orchestrateur
│   ├── prepare_owid_data.py             # Préparation données
│   ├── analysis_examples.py             # Exemples d'analyse
│   └── utils.py
│
├── docker/
│   ├── docker-compose.yml
│   └── Dockerfile
│
├── notebooks/
│   └── 00-data-exploration.ipynb
│
├── PREPROCESSING_ARCHITECTURE.md        # Architecture Medallion
├── OWID_INTEGRATION_GUIDE.md           # Intégration OWID
├── IMPLEMENTATION_SUMMARY.md            # Résumé implémentation
└── README.md
```

---

## Commandes Importantes

### Lire les Données Nettoyées (Silver)

```python
spark = SparkSession.builder.appName("Read").getOrCreate()

# Vaccination nettoyée
vax = spark.read.parquet("s3a://silver/vaccination_cleaned/")
print(f"Records: {vax.count()}")
vax.printSchema()

# Mortalité nettoyée
mort = spark.read.parquet("s3a://silver/mortality_cleaned/")

# Tests nettoyés
test = spark.read.parquet("s3a://silver/testing_cleaned/")

# Cas nettoyés
cases = spark.read.parquet("s3a://silver/cases_cleaned/")
```

### Lire les Données Agrégées (Gold)

```python
# Vaccination mensuelle
vax_monthly = spark.read.parquet("s3a://gold/vaccination_monthly/")

# Vaccination par pays
vax_by_country = spark.read.parquet("s3a://gold/vaccination_by_location/")

# Mortalité mensuelle
mort_monthly = spark.read.parquet("s3a://gold/mortality_monthly/")

# Etc...
```

### Analyser Rapidement

```python
# Top 5 pays avec plus de vaccinations complètes
vax_by_country.select("location", "max_fully_vaccinated") \
    .orderBy(desc("max_fully_vaccinated")) \
    .limit(5) \
    .show()

# Joindre vaccination et mortalité
combined = vax_monthly.join(
    mort_monthly,
    on=["location", "year", "month"]
)
```

---

## Dépannage Rapide

| Problème | Solution |
|----------|----------|
| "File not found" | Vérifier que les fichiers CSV sont bien uploadés dans le bucket bronze de MinIO |
| "Missing columns" | Vérifier que owid-covid-data.csv contient les colonnes attendues |
| Spark ne démarre pas | Vérifier: `docker compose logs spark` et disponibilité mémoire |
| MinIO inaccessible | Vérifier port 9001 et credentials (minioadmin/minioadmin) |
| Pipeline très lent | Pour test, filtrer un seul pays avec `prepare_owid_data.py --country` |

---

## Résultats Attendus

### Après process_data.py (Bronze → Silver)

```
Processing s3a://bronze/vaccination.csv...
Initial record count: 10,234,567
All required columns present
Removed 45,123 rows with null dates
Removed 12,456 duplicate rows
...
Final record count: 9,876,234 (96.5%)
Writing to s3a://silver/vaccination_cleaned/
```

### Après aggregate_data.py (Silver → Gold)

```
Aggregating Vaccination Data (Monthly)
Read 9,876,234 records
Vaccination monthly aggregation: 2,847 records
Writing to s3a://gold/vaccination_monthly/

Aggregating Vaccination Data (By Location)
Vaccination by location aggregation: 195 records
Writing to s3a://gold/vaccination_by_location/

[Même pour mortality, testing, cases...]
```

---

## Utiliser les Données en Production

### Notebook Jupyter

```python
# Dans notebooks/
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("COVID19 Analysis").getOrCreate()

# Charger données Gold
vax = spark.read.parquet("s3a://gold/vaccination_monthly/")
mort = spark.read.parquet("s3a://gold/mortality_monthly/")

# Analyse
df_combined = vax.join(mort, ["location", "year", "month"])
df_combined.write.parquet("s3a://gold/combined_analysis/")
```

### Dashboard (avec Plotly/Dash)

```python
import plotly.express as px
import pandas as pd

# Convertir Spark DF en Pandas
df_vax = vax.toPandas()

# Créer visualisation
fig = px.line(df_vax, x="date", y="max_fully_vaccinated", 
              color="location", title="Vaccination Trends")
fig.show()
```

### Machine Learning (avec MLlib)

```python
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import LinearRegression

# Préparer features
vectorizer = VectorAssembler(
    inputCols=["max_deaths", "max_cases"],
    outputCol="features"
)

# Entraîner modèle
lr = LinearRegression()
model = lr.fit(vectorizer.transform(combined))
```

---

## Documentation Complète

Pour plus de détails:
- **Architecture**: Lire `PREPROCESSING_ARCHITECTURE.md`
- **Intégration OWID**: Lire `OWID_INTEGRATION_GUIDE.md`
- **Résumé implémentation**: Lire `IMPLEMENTATION_SUMMARY.md`

---

## Fichiers Python Clés

| Fichier | Responsabilité | Commande |
|---------|----------------|----------|
| prepare_owid_data.py | Diviser données par type | `python scripts/prepare_owid_data.py --input ... --output ...` |
| process_data.py | Nettoyer (Bronze → Silver) | `python scripts/process_data.py` |
| aggregate_data.py | Agréger (Silver → Gold) | `python scripts/aggregate_data.py` |
| run_pipeline.py | Pipeline complet | `python scripts/run_pipeline.py` |
| analysis_examples.py | Exemples d'analyse | `python scripts/analysis_examples.py` |

---

## Status du Pipeline

- Bronze Layer: Données brutes OWID en CSV
- Silver Layer: Données nettoyées en Parquet
- Gold Layer: Données agrégées prêtes pour analyse

**Prêt pour**: Reports, dashboards, machine learning, analyses statistiques

---

**Ready to analyze!** 🚀
