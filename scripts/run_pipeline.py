import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.minio_utils import create_buckets
from scripts.ingest_data import ingest_bronze_data
from scripts.process_data import run_bronze_to_silver_pipeline
from scripts.aggregate_data import run_silver_to_gold_pipeline

def main():
    """
    Execute the complete COVID-19 data processing pipeline.
    
    Pipeline stages:
    1. Bronze Layer: Raw CSV files from OWID
    2. Silver Layer: Cleaned, validated, deduplicated data
    3. Gold Layer: Aggregated data ready for analysis
    """
    
    print("\n" + "="*70)
    print("COVID-19 DATA PROCESSING PIPELINE")
    print("="*70)
    
    try:
        # Stage 0: Ensure Bronze data is available in MinIO
        print("\n[STAGE 0/3] Creating buckets and ingesting Bronze data...")
        print("-" * 70)
        create_buckets()
        ingest_bronze_data()

        # Stage 1: Bronze to Silver - Cleaning and Validation
        print("\n[STAGE 1/3] Starting Bronze to Silver transformation...")
        print("-" * 70)
        run_bronze_to_silver_pipeline()
        
        # Stage 2: Silver to Gold - Aggregation and Analysis Prep
        print("\n[STAGE 2/3] Starting Silver to Gold transformation...")
        print("-" * 70)
        run_silver_to_gold_pipeline()
        
        print("\n" + "="*70)
        print("PIPELINE COMPLETED SUCCESSFULLY")
        print("="*70)
        print("\nData is now ready for analysis:")
        print("- Monthly aggregations available in gold/vaccination_monthly/")
        print("- Monthly aggregations available in gold/mortality_monthly/")
        print("- Monthly aggregations available in gold/testing_monthly/")
        print("- Monthly aggregations available in gold/cases_monthly/")
        print("- Location-level summaries available in gold/*_by_location/")
        print("="*70 + "\n")
        
    except Exception as e:
        print("\n" + "="*70)
        print("PIPELINE FAILED")
        print("="*70)
        print(f"Error: {e}")
        print("="*70 + "\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
