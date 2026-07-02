from pathlib import Path
from dotenv import load_dotenv
import os


def load_env() -> dict:
    env_path = Path(".env")
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)

    return {
        "MINIO_ROOT_USER": os.getenv("MINIO_ROOT_USER", "minioadmin"),
        "MINIO_ROOT_PASSWORD": os.getenv("MINIO_ROOT_PASSWORD", "minioadmin"),
        "MINIO_BUCKET_BRONZE": os.getenv("MINIO_BUCKET_BRONZE", "bronze"),
        "MINIO_BUCKET_SILVER": os.getenv("MINIO_BUCKET_SILVER", "silver"),
        "MINIO_BUCKET_GOLD": os.getenv("MINIO_BUCKET_GOLD", "gold"),
        "MINIO_HOST": os.getenv("MINIO_HOST", "localhost"),
        "MINIO_PORT": os.getenv("MINIO_PORT", "9000"),
        "SPARK_APP_NAME": os.getenv("SPARK_APP_NAME", "CovidDataAnalysis"),
    }
