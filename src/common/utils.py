from pathlib import Path
from dotenv import load_dotenv
import os


def _require_env(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise EnvironmentError(f"Missing required environment variable: {key}")
    return value


def load_env() -> dict:
    env_path = Path(".env")
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)

    return {
        "MINIO_ROOT_USER": _require_env("MINIO_ROOT_USER"),
        "MINIO_ROOT_PASSWORD": _require_env("MINIO_ROOT_PASSWORD"),
        "MINIO_BUCKET_BRONZE": _require_env("MINIO_BUCKET_BRONZE"),
        "MINIO_BUCKET_SILVER": _require_env("MINIO_BUCKET_SILVER"),
        "MINIO_BUCKET_GOLD": _require_env("MINIO_BUCKET_GOLD"),
        "MINIO_HOST": _require_env("MINIO_HOST"),
        "MINIO_PORT": _require_env("MINIO_PORT"),
        "SPARK_APP_NAME": _require_env("SPARK_APP_NAME"),
        "COVID_DATA_URL": os.getenv("COVID_DATA_URL"),
        "COVID_DATA_FILE": os.getenv("COVID_DATA_FILE"),
    }
