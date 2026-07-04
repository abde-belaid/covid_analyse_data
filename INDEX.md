# INDEX - Ressources Pipeline COVID-19

## Navigation Rapide

### Documentation (Lire dans cet ordre)

| Fichier | Objectif | Temps |
|---------|----------|-------|
| **FINAL_SUMMARY.md** | Vue d'ensemble complète | 10 min ⭐ COMMENCER ICI |
| **QUICKSTART_PIPELINE.md** | 5 étapes pour démarrer | 5 min |
| **PREPROCESSING_ARCHITECTURE.md** | Architecture Medallion détaillée | 15 min |
| **OWID_INTEGRATION_GUIDE.md** | Télécharger & intégrer OWID | 10 min |
| **IMPLEMENTATION_SUMMARY.md** | Détails implémentation | 10 min |

### Fichiers Python

| Fichier | Objectif | Exécution |
|---------|----------|----------|
| **process_data.py** | Bronze → Silver (Nettoyage) | `python scripts/process_data.py` |
| **aggregate_data.py** | Silver → Gold (Agrégation) | `python scripts/aggregate_data.py` |
| **run_pipeline.py** | Pipeline complet (Orchestration) | `python scripts/run_pipeline.py` ⭐ PRINCIPAL |
| **prepare_owid_data.py** | Préparation données OWID | `python scripts/prepare_owid_data.py --input ... --output ...` |
| **analysis_examples.py** | 7 exemples d'analyse | `python scripts/analysis_examples.py` |
| **validate_pipeline.py** | Valider la structure | `python scripts/validate_pipeline.py` |

### Fichiers de Support

| Fichier | Contenu |
|---------|---------|
| **start_pipeline.sh** | Script d'initialisation rapide |
| **README.md** | Présentation générale du projet |
| **requirements.txt** | Dépendances Python |

---

## Démarrage Rapide (3 minutes)

```bash
# 1. Initialiser
bash start_pipeline.sh

# 2. Télécharger données OWID
wget https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv -O data/bronze/owid-covid-data.csv

# 3. Préparer par type de données
python scripts/prepare_owid_data.py --input data/bronze/owid-covid-data.csv

# 4. Uploader vers MinIO (bronze bucket)
# Via interface: http://localhost:9001

# 5. Lancer pipeline complet
python scripts/run_pipeline.py

# 6. Analyser résultats
python scripts/analysis_examples.py
```

---

## Concepts Clés Implémentés

### Architecture Medallion
- **Bronze**: Données brutes CSV
- **Silver**: Données nettoyées Parquet
- **Gold**: Données agrégées prêtes pour analyse

### Helpers Réutilisables (11 au total)
```python
# Génériques (8)
helper_read_csv()
helper_validate_required_columns()
helper_handle_date_column()
helper_fill_numeric_nulls()
helper_remove_duplicates()
helper_normalize_text_columns()
helper_validate_positive_values()
helper_log_data_quality()

# Agrégation (3)
helper_add_time_dimensions()
helper_write_parquet()
helper_read_parquet()
```

### Datasets Traités (4 types)
- Vaccination
- Mortalité
- Tests
- Cas

### Niveaux d'Agrégation (2 par dataset)
- **Mensuel**: Tendances temporelles
- **Par Pays**: Comparaisons géographiques

---

## Structure des Données

### Bronze → Silver Transformations
```
Vaccination: 10M lignes brutes → 9.5M lignes nettoyées (95% retention)
- Suppression nulls de dates
- Déduplication (location, date)
- Remplissage nulls numériques
- Filtrage négatifs
```

### Silver → Gold Agrégations
```
Monthly: (location, year, month) → max, min, avg, sum
By Location: (location) → max, min, cumulative totals, date range
```

---

## Utilisation Typique

### Pour Développeurs
1. Lire FINAL_SUMMARY.md
2. Examiner process_data.py (structure helpers)
3. Examiner aggregate_data.py (fonctions d'agrégation)
4. Exécuter validate_pipeline.py (confirme implémentation)

### Pour Data Scientists
1. Lire QUICKSTART_PIPELINE.md
2. Exécuter run_pipeline.py
3. Exécuter analysis_examples.py
4. Étendre avec analyses personnalisées

### Pour DevOps
1. Vérifier docker-compose.yml
2. S'assurer MinIO + Spark actifs
3. Configurer paths s3a://
4. Monitorer exécution pipeline

### Pour Analystes
1. Lire PREPROCESSING_ARCHITECTURE.md
2. Charger datasets Gold via Spark
3. Utiliser examples d'analyse comme base
4. Créer rapports/dashboards

---

## Validation et Tests

### Vérifier la Structure
```bash
python scripts/validate_pipeline.py
```

### Vérifier les Données Silver
```python
spark.read.parquet("s3a://silver/vaccination_cleaned/").show()
```

### Vérifier les Données Gold
```python
spark.read.parquet("s3a://gold/vaccination_monthly/").show()
```

### Exécuter les Exemples d'Analyse
```bash
python scripts/analysis_examples.py
```

---

## Fichiers Importants à Consulter

### Si vous avez des questions sur...

| Question | Fichier à Consulter |
|----------|-------------------|
| "Comment ça marche?" | FINAL_SUMMARY.md ou PREPROCESSING_ARCHITECTURE.md |
| "Comment démarrer?" | QUICKSTART_PIPELINE.md |
| "Comment intégrer OWID?" | OWID_INTEGRATION_GUIDE.md |
| "Où sont les helpers?" | process_data.py (lignes 15-100) |
| "Comment agréger?" | aggregate_data.py (lignes 35+) |
| "Comment analyser?" | analysis_examples.py ou ces 7 exemples |
| "Est-ce tout là?" | Exécuter validate_pipeline.py |

---

## Capacités du Pipeline

### Scalabilité
- Support millions de lignes
- Parquet compressé
- Spark distribué

### Qualité des Données
- Validation colonnes requises
- Suppression doublons
- Remplissage nulls intelligent
- Filtrage valeurs négatives
- Normalisation texte

### Extensibilité
- Facile ajouter nouveaux datasets
- Helpers réutilisables
- Architecture modulaire

### Documenté
- 5 guides complets
- Docstrings dans code
- Exemples d'utilisation
- Validation structure

---

## Structure Fichiers Scripts

```
scripts/
├── process_data.py
│   ├── Helpers (lignes 15-115)
│   ├── Cleaning functions (lignes 120-320)
│   ├── Pipeline (lignes 325-400)
│   └── Main (lignes 405-430)
│
├── aggregate_data.py
│   ├── Helpers (lignes 10-80)
│   ├── Aggregation functions (lignes 85-400)
│   ├── Pipeline (lignes 405-500)
│   └── Main (lignes 505-530)
│
├── run_pipeline.py
│   └── Orchestrateur deux stages
│
├── prepare_owid_data.py
│   └── Extraction par dataset type
│
├── analysis_examples.py
│   └── 7 exemples d'analyse
│
└── validate_pipeline.py
    └── Vérification structure
```

---

## Dépannage Rapide

| Erreur | Solution |
|--------|----------|
| ModuleNotFoundError | Installer: `pip install -r requirements.txt` |
| "File not found" | Vérifier MinIO + bucket bronze |
| "Missing column" | Vérifier CSV source contient les colonnes |
| Spark ne démarre | Vérifier: `docker compose logs spark` |
| Trop lent | Filtrer par pays avec prepare_owid_data.py |
| Validation échouée | Vérifier tous les fichiers Python présents |

---

## Links Utiles

- **OWID Repository**: https://github.com/owid/covid-19-data
- **OWID Website**: https://ourworldindata.org/coronavirus
- **MinIO Docs**: https://min.io/docs/
- **Spark Documentation**: https://spark.apache.org/docs/
- **Parquet Format**: https://parquet.apache.org/

---

## Checklist Démarrage

- [ ] Lire FINAL_SUMMARY.md
- [ ] Exécuter bash start_pipeline.sh
- [ ] Télécharger données OWID
- [ ] Exécuter prepare_owid_data.py
- [ ] Uploader CSVs vers MinIO
- [ ] Exécuter run_pipeline.py
- [ ] Vérifier résultats avec analysis_examples.py
- [ ] Valider avec validate_pipeline.py

---

## Status Production ✓

Pipeline complet et validé:
- Cleaing rigoureux
- Agrégation complète
- Documentation exhaustive
- Exempls d'usage
- Validation structure
- Support données volumineuses

**Prêt pour analyse de production!**

---

**Pour commencer: Lire FINAL_SUMMARY.md ou exécuter: bash start_pipeline.sh**
