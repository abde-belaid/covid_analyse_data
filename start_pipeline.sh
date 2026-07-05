#!/bin/bash
# COVID-19 Data Processing Pipeline - Quick Start Script
# Usage: bash start_pipeline.sh

set -e

echo "======================================================================"
echo "COVID-19 DATA PROCESSING PIPELINE - INITIALIZATION"
echo "======================================================================"

PROJECT_DIR="/home/belaid-abderrahim/Bureau/Master/S2/Big Data/tps/covid_data_analysis"
SCRIPTS_DIR="$PROJECT_DIR/scripts"
DATA_DIR="$PROJECT_DIR/data/bronze"

cd "$PROJECT_DIR"

echo ""
echo "[STEP 1/5] Validation de la structure du pipeline..."
echo "======================================================================"
python "$SCRIPTS_DIR/validate_pipeline.py"

echo ""
echo "[STEP 2/5] Préparation des répertoires..."
echo "======================================================================"
mkdir -p "$DATA_DIR"
echo "✓ Répertoire data/bronze créé"

echo ""
echo "[STEP 3/5] Vérification des dépendances..."
echo "======================================================================"
python3 -c "
import sys
modules = ['pyspark', 'pandas', 'boto3']
missing = []
for module in modules:
    try:
        __import__(module)
        print(f'✓ {module} disponible')
    except ImportError:
        missing.append(module)
        print(f'✗ {module} manquant')

if missing:
    print(f'\nModules manquants: {missing}')
    print('À installer: pip install ' + ' '.join(missing))
    sys.exit(1)
"

echo ""
echo "[STEP 4/5] Information sur les fichiers OWID..."
echo "======================================================================"
echo ""
echo "Vous pouvez obtenir les données OWID COVID-19 de 3 façons:"
echo ""
echo "Option 1: Télécharger le dataset complet (500MB)"
echo "  wget https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv -O data/bronze/owid-covid-data.csv"
echo ""
echo "Option 2: Via git clone"
echo "  git clone https://github.com/owid/covid-19-data.git"
echo "  cp owid-covid-19-data/public/data/owid-covid-data.csv data/bronze/"
echo ""
echo "Option 3: Télécharger depuis le site OWID"
echo "  https://ourworldindata.org/coronavirus"
echo ""

echo "[STEP 5/5] Fichiers de démarrage prêts!"
echo "======================================================================"
echo ""
echo "Prochaines étapes:"
echo ""
echo "1. Préparation des données OWID:"
echo "   python scripts/prepare_owid_data.py --input data/bronze/owid-covid-data.csv"
echo ""
echo "2. Upload vers MinIO (bucket: bronze)"
echo "   Accéder: http://localhost:9001"
echo "   Credentials: minioadmin / minioadmin"
echo ""
echo "3. Exécuter le pipeline complet:"
echo "   python scripts/run_pipeline.py"
echo ""
echo "4. Analyser les résultats:"
echo "   python scripts/analysis_examples.py"
echo ""
echo "======================================================================"
echo "Documentation disponible:"
echo "  - QUICKSTART_PIPELINE.md       (Démarrage rapide)"
echo "  - PREPROCESSING_ARCHITECTURE.md (Architecture complète)"
echo "  - OWID_INTEGRATION_GUIDE.md     (Intégration OWID)"
echo "  - FINAL_SUMMARY.md              (Résumé complet)"
echo "======================================================================"
echo ""
echo "Pipeline prêt pour le traitement des données COVID-19!"
echo ""
