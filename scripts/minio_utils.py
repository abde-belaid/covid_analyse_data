# dans cette partie je veux creer un script qui va me permettre de creer un bucket minio et d'y charger les données du fichier covid_data.csv
import sys
from pathlib import Path
import os
from dotenv import load_dotenv
from minio import Minio

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

env_path = ROOT_DIR / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

minio_client = Minio(
    endpoint=os.getenv("MINIO_HOST", "localhost") + ":" + os.getenv("MINIO_PORT", "9000"),
    access_key=os.getenv("MINIO_ROOT_USER"),
    secret_key=os.getenv("MINIO_ROOT_PASSWORD"),
    secure=False # secure=False car nous utilisons HTTP pour MinIO en local
)

def create_buckets():
    
    bucket_names = [os.getenv("MINIO_BUCKET_BRONZE", "bronze"), os.getenv("MINIO_BUCKET_SILVER", "silver"), os.getenv("MINIO_BUCKET_GOLD", "gold")]
    
    for bucket_name in bucket_names:
        
        if not minio_client.bucket_exists(bucket_name):
            minio_client.make_bucket(bucket_name)
            print(f"Bucket '{bucket_name}' créé avec succès.")

        else:
            print(f"Bucket '{bucket_name}' existe déjà.")