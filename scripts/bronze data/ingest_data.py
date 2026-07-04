import os
import sys
import requests
import io
from pathlib import Path
from minio import Minio

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.utils import load_env

def ingest_covid_data_to_bronze_bucket():
    """
    Downloads COVID-19 data (Morocco vaccinations) and uploads it to the Bronze bucket in MinIO.
    """
    env = load_env()
    
    minio_client = Minio(
        endpoint=f'{env.get("MINIO_HOST", "localhost")}:{env.get("MINIO_PORT", "9000")}',
        access_key=env.get("MINIO_ROOT_USER"),
        secret_key=env.get("MINIO_ROOT_PASSWORD"),
        secure=False
    )
    
    bucket_name = env.get("MINIO_BUCKET_BRONZE", "bronze")
    
    # Ensure bucket exists
    if not minio_client.bucket_exists(bucket_name):
        minio_client.make_bucket(bucket_name)
        print(f"Created bucket '{bucket_name}'")

    # The URL provided by the user (raw version)
    url = env.get("COVID_DATA_URL", "https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/country_data/Morocco.csv")
    fichier_vaccination = env.get("COVID_DATA_FILE", "covid_data_morocco.csv")
    fichier_mortality = env.get("MORTALITY_DATA_FILE", "covid_data_morocco_mortality.csv")  # Assuming you have a mortality CSV file as well
    fichier_testing = env.get("TESTING_DATA_FILE", "covid_data_morocco_testing.csv")  # Assuming you have a testing CSV file as well



    print(f"Downloading COVID-19 data from {url}...")
    response = requests.get(url)
    response.raise_for_status() # Raise an error for bad responses
    
    data = response.content
    data_stream = io.BytesIO(data) # Create a BytesIO stream from the downloaded data (BytesIO is used for binary data, while StringIO is used for text data)
    data_length = len(data)
    
    print(f"Uploading data to MinIO bucket '{bucket_name}' as '{fichier_vaccination}'...")
    minio_client.put_object(
        bucket_name,
        fichier_vaccination,
        data_stream,
        data_length,
        content_type="text/csv"
    )
    print("Ingestion completed successfully!")

if __name__ == "__main__":
    ingest_covid_data_to_bronze_bucket()
