# MinIO bucket management using only environment variables from .env
import sys
from pathlib import Path
from minio import Minio

from src.common.utils import load_env


def _build_minio_client(env):
    endpoint = f"{env['MINIO_HOST']}:{env['MINIO_PORT']}"
    return Minio(
        endpoint=endpoint,
        access_key=env['MINIO_ROOT_USER'],
        secret_key=env['MINIO_ROOT_PASSWORD'],
        secure=False,
    )


def create_buckets():
    env = load_env()
    minio_client = _build_minio_client(env)

    bucket_names = [
        env['MINIO_BUCKET_BRONZE'],
        env['MINIO_BUCKET_SILVER'],
        env['MINIO_BUCKET_GOLD'],
    ]

    for bucket_name in bucket_names:
        if not minio_client.bucket_exists(bucket_name):
            minio_client.make_bucket(bucket_name)
            print(f"Bucket '{bucket_name}' créé avec succès.")
        else:
            print(f"Bucket '{bucket_name}' existe déjà.")
