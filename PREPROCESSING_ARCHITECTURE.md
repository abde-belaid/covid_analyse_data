# Architecture de Preprocessing des Données COVID-19

## Vue d'ensemble

Le pipeline de preprocessing suit l'architecture **Medallion** (Bronze → Silver → Gold) pour transformer les données brutes OWID en données d'analyse propres et agrégées.

```
Bronze Layer (Raw CSV)
    ↓
    ├── vaccination.csv
    ├── mortality.csv
    ├── testing.csv
    └── cases.csv
    ↓
[CLEANING & VALIDATION - process_data.py]
    ↓
Silver Layer (Cleaned Parquet)
    ├── vaccination_cleaned/
    ├── mortality_cleaned/
    ├── testing_cleaned/
    └── cases_cleaned/
    ↓
[AGGREGATION - aggregate_data.py]
    ↓
Gold Layer (Aggregated Parquet - Ready for Analysis)
    ├── vaccination_monthly/
    ├── vaccination_by_location/
    ├── mortality_monthly/
    ├── mortality_by_location/
    ├── testing_monthly/
    ├── testing_by_location/
    ├── cases_monthly/
    └── cases_by_location/
```

## Fichiers du Pipeline

### 1. process_data.py (Bronze → Silver)

**Responsabilité**: Lecture des fichiers CSV bruts, nettoyage rigoureux et validation.

**Fonctions Helper** (réutilisables):
- `helper_read_csv()` - Lecture CSV avec gestion d'erreurs
- `helper_validate_required_columns()` - Validation des colonnes requises
- `helper_handle_date_column()` - Conversion et validation des dates
- `helper_fill_numeric_nulls()` - Remplissage des valeurs nulles numériques
- `helper_remove_duplicates()` - Suppression des doublons
- `helper_normalize_text_columns()` - Normalisation du texte (trim, uppercase)
- `helper_validate_positive_values()` - Filtrage des valeurs négatives
- `helper_log_data_quality()` - Rapport de qualité des données

**Fonctions de Nettoyage Spécifiques**:
- `clean_vaccination_data()` - Nettoyage des données de vaccination
- `clean_mortality_data()` - Nettoyage des données de mortalité
- `clean_testing_data()` - Nettoyage des données de tests
- `clean_cases_data()` - Nettoyage des données de cas

**Processus par dataset**:
1. Lecture du CSV depuis Bronze
2. Normalisation du texte (location, iso_code)
3. Conversion et filtrage des dates
4. Déduplication basée sur (location, date)
5. Remplissage des nulls numériques avec 0
6. Filtrage des valeurs négatives
7. Tri pour la cohérence
8. Rapport de qualité
9. Écriture en Parquet dans Silver

**Exécution**:
```python
python scripts/process_data.py
```

---

### 2. aggregate_data.py (Silver → Gold)

**Responsabilité**: Lecture des fichiers Parquet nettoyés, agrégation et préparation pour l'analyse.

**Fonctions Helper**:
- `helper_add_time_dimensions()` - Ajout des dimensions temporelles (year, month, quarter, day_of_year)
- `helper_write_parquet()` - Écriture Parquet avec gestion d'erreurs
- `helper_read_parquet()` - Lecture Parquet avec gestion d'erreurs

**Agrégations par Dataset**:

#### Vaccination
- `aggregate_vaccination_monthly()` - Agrégation mensuelle (max, avg, min par mois)
- `aggregate_vaccination_by_location()` - Résumé au niveau du pays

#### Mortalité
- `aggregate_mortality_monthly()` - Agrégation mensuelle (max, somme, moyenne)
- `aggregate_mortality_by_location()` - Résumé au niveau du pays

#### Tests
- `aggregate_testing_monthly()` - Agrégation mensuelle (max, somme, moyenne, taux positif)
- `aggregate_testing_by_location()` - Résumé au niveau du pays

#### Cas
- `aggregate_cases_monthly()` - Agrégation mensuelle (max, somme, moyenne)
- `aggregate_cases_by_location()` - Résumé au niveau du pays

**Exécution**:
```python
python scripts/aggregate_data.py
```

---

### 3. run_pipeline.py (Orchestrateur)

**Responsabilité**: Exécution du pipeline complet Bronze → Silver → Gold en séquence.

**Exécution du pipeline complet**:
```bash
python scripts/run_pipeline.py
```

---

## Structure des Données

### Bronze Layer (Fichiers CSV)
Colonnes attendues par dataset:

**vaccination.csv**:
- iso_code, location, date, total_vaccinations, people_vaccinated, people_fully_vaccinated, people_boosted

**mortality.csv**:
- iso_code, location, date, total_deaths, new_deaths

**testing.csv**:
- iso_code, location, date, total_tests, new_tests, tests_per_case, positive_rate

**cases.csv**:
- iso_code, location, date, total_cases, new_cases

### Silver Layer (Parquet)
Données nettoyées et déduplicatées:
- Toutes les valeurs nulles remplies pour les colonnes numériques
- Doublons supprimés
- Dates normalisées
- Texte normalisé
- Valeurs négatives filtrées

### Gold Layer (Parquet)
Données agrégées prêtes pour l'analyse:
- Agrégations mensuelles avec max, min, avg, sum
- Agrégations au niveau du pays avec statistiques globales
- Dimensions temporelles enrichies (year, month, quarter, etc.)

---

## Pratiques Implémentées

### 1. Modularité
- Chaque type de données a ses propres fonctions de nettoyage
- Helpers réutilisables pour éviter la redondance
- Séparation des responsabilités (cleaning vs aggregation)

### 2. Gestion d'Erreurs
- Try/catch pour la lecture de fichiers
- Validation des colonnes requises
- Messages d'erreur descriptifs

### 3. Logging et Monitoring
- Rapports de qualité des données à chaque étape
- Comptage des lignes supprimées/transformées
- Pourcentage de réduction visible

### 4. Scalabilité
- Structure compatible avec des millions de lignes
- Utilisation de Spark pour le traitement distribué
- Écriture en Parquet pour optimisation des lectures futures

### 5. Qualité des Données
- Validation des valeurs positives
- Suppression des doublons
- Remplissage intelligent des nulls
- Normalisation du texte

---

## Exemple de Flux Complet

```
1. Fichier Bronze: vaccination.csv (10M lignes)
   └─ Lecture CSV
   └─ Nettoyage (normalisation, dates, doublons)
   └─ Validation (positives, nulls)
   └─ Écriture Silver: vaccination_cleaned/ (8.5M lignes - 15% supprimés)

2. Fichier Silver: vaccination_cleaned/
   └─ Lecture Parquet
   └─ Ajout dimensions temporelles
   └─ Agrégation mensuelle
   └─ Écriture Gold: vaccination_monthly/ (prêt pour analyse)
   └─ Agrégation par pays
   └─ Écriture Gold: vaccination_by_location/ (195 pays)
```

---

## Utilisation dans l'Analyse

Après exécution du pipeline, accédez aux données pour l'analyse:

```python
# Lecture des données agrégées
spark = SparkSession.builder.appName("Analysis").getOrCreate()

df_vax_monthly = spark.read.parquet("s3a://gold/vaccination_monthly/")
df_mort_monthly = spark.read.parquet("s3a://gold/mortality_monthly/")
df_test_monthly = spark.read.parquet("s3a://gold/testing_monthly/")
df_cases_monthly = spark.read.parquet("s3a://gold/cases_monthly/")

# Analyse combinée
df_vax_monthly.join(df_mort_monthly, ["location", "year", "month"]) \
    .join(df_test_monthly, ["location", "year", "month"]) \
    .show()
```

---

## Notes Importantes

1. **Colonnes Dynamiques**: Les fonctions gèrent les colonnes manquantes avec des fallbacks appropriés
2. **Doublons**: Suppression basée sur (location, date) pour éviter les enregistrements dupliqués
3. **Valeurs Nulles**: Pour les numériques, remplissage avec 0 (acceptable pour les data OWID)
4. **Performance**: Les traitements exploitent la parallelisation de Spark
5. **Stockage MinIO**: Chemins s3a:// pour intégration MinIO

---

## Commandes Rapides

```bash
# Exécuter le pipeline complet
python scripts/run_pipeline.py

# Exécuter seulement Bronze → Silver
python scripts/process_data.py

# Exécuter seulement Silver → Gold
python scripts/aggregate_data.py

# Vérifier les données nettoyées
spark-shell
> spark.read.parquet("s3a://silver/vaccination_cleaned/").count()
```
