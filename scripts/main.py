import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.minio_utils import create_buckets
from scripts.ingest_data import ingest_covid_data
from scripts.process_data import run_processing_pipeline

def main():
    print("="*50)
    print("Starting Covid-19 Data Analysis Pipeline")
    print("="*50)
    
    try:
        print("\n[Step 1] Creating MinIO buckets (if they do not exist)...")
        create_buckets()
        
        print("\n[Step 2] Ingesting data to Bronze layer...")
        ingest_covid_data()
        
        print("\n[Step 3] Processing data (Bronze -> Silver -> Gold)...")
        run_processing_pipeline()
        
        print("\n" + "="*50)
        print("✅ Pipeline executed successfully!")
        print("="*50)
        
    except Exception as e:
        print("\n" + "="*50)
        print(f"❌ Pipeline failed: {e}")
        print("="*50)
        sys.exit(1)

if __name__ == "__main__":
    main()
