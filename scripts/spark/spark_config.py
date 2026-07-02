import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from pyspark.sql import SparkSession
import logging

ROOT_DIR = Path(__file__).resolve().parents[2]
env_path = ROOT_DIR / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    logging.warning(f".env file not found at {env_path}")

logging.basicConfig(level=logging.INFO)


def create_spark_session():
    app_name = os.getenv("SPARK_APP_NAME", "CovidDataAnalysis")
    minio_endpoint = os.getenv("MINIO_ENDPOINT", "http://localhost:9000")
    minio_access_key = os.getenv("MINIO_ROOT_USER", "minioadmin")
    minio_secret_key = os.getenv("MINIO_ROOT_PASSWORD", "minioadmin")

    try:
        spark = (
            SparkSession.builder
            .appName(app_name)
            .config("spark.hadoop.fs.s3a.endpoint", minio_endpoint)
            .config("spark.hadoop.fs.s3a.access.key", minio_access_key)
            .config("spark.hadoop.fs.s3a.secret.key", minio_secret_key)
            .config("spark.hadoop.fs.s3a.path.style.access", "true")
            .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false")
            .config("spark.hadoop.fs.s3a.aws.credentials.provider", "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider")
            .config("spark.hadoop.fs.s3a.connection.establish.timeout", "5000")
            .config("spark.hadoop.fs.s3a.connection.timeout", "50000")
            .config("spark.hadoop.fs.s3a.threads.keepalivetime", "60000")
            .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
            .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.4.2,software.amazon.awssdk:bundle:2.29.52")
            .getOrCreate()
        )
        print(f"Spark session created with app name: {app_name}")
    except Exception as e:
        logging.error(f"Error creating Spark session: {e}")
        raise
    return spark