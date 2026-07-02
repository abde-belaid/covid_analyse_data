import os
import sys
from pathlib import Path
from pyspark.sql.functions import col, month, year, max as spark_max

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.spark.spark_config import create_spark_session
from scripts.utils import load_env

def process_bronze_to_silver(spark, env):
    """
    Reads raw CSV data from the Bronze bucket, cleans it, and writes it to the Silver bucket in Parquet format.
    """
    bronze_bucket = env.get("MINIO_BUCKET_BRONZE", "bronze")
    silver_bucket = env.get("MINIO_BUCKET_SILVER", "silver")
    
    bronze_path = f"s3a://{bronze_bucket}/covid_data_morocco.csv"
    silver_path = f"s3a://{silver_bucket}/covid_data_morocco_cleaned"
    
    print(f"Reading raw data from {bronze_path}...")
    df = spark.read.csv(bronze_path, header=True, inferSchema=True)
    
    print("Cleaning data...")
    # Clean data: drop rows where date is null
    df_cleaned = df.dropna(subset=["date"])
    
    # Fill nulls with 0 for numeric columns to avoid issues in aggregation
    numeric_columns = ["total_vaccinations", "people_vaccinated", "people_fully_vaccinated"]
    df_cleaned = df_cleaned.fillna(0, subset=[c for c in numeric_columns if c in df_cleaned.columns])
    
    print(f"Writing cleaned data to {silver_path} in Parquet format...")
    df_cleaned.write.mode("overwrite").parquet(silver_path)
    
    return df_cleaned

def process_silver_to_gold(spark, env):
    """
    Reads cleaned Parquet data from the Silver bucket, aggregates it, and writes to the Gold bucket.
    """
    silver_bucket = env.get("MINIO_BUCKET_SILVER", "silver")
    gold_bucket = env.get("MINIO_BUCKET_GOLD", "gold")
    
    silver_path = f"s3a://{silver_bucket}/covid_data_morocco_cleaned"
    gold_path = f"s3a://{gold_bucket}/vaccination_monthly_summary"
    
    print(f"Reading cleaned data from {silver_path}...")
    df = spark.read.parquet(silver_path)
    
    print("Aggregating data...")
    # Ensure date column is properly cast to date or timestamp if it's not already
    df = df.withColumn("date", col("date").cast("date"))
    
    # Monthly aggregation to find the max people fully vaccinated per month
    if "people_fully_vaccinated" in df.columns:
        df_gold = (
            df.withColumn("year", year(col("date")))
              .withColumn("month", month(col("date")))
              .groupBy("year", "month")
              .agg(spark_max("people_fully_vaccinated").alias("max_fully_vaccinated"))
              .orderBy("year", "month")
        )
    else:
        # Fallback if the column is missing
        print("Column 'people_fully_vaccinated' not found, using count instead.")
        df_gold = (
            df.withColumn("year", year(col("date")))
              .withColumn("month", month(col("date")))
              .groupBy("year", "month")
              .count()
              .orderBy("year", "month")
        )
    
    print(f"Writing aggregated data to {gold_path} in Parquet format...")
    df_gold.write.mode("overwrite").parquet(gold_path)
    
    print("Sample of Gold data:")
    df_gold.show(truncate=False)

def run_processing_pipeline():
    env = load_env()
    print("Initializing Spark session...")
    spark = create_spark_session()
    
    try:
        process_bronze_to_silver(spark, env)
        process_silver_to_gold(spark, env)
        print("Data processing pipeline completed successfully.")
    except Exception as e:
        print(f"An error occurred during data processing: {e}")
        raise
    finally:
        spark.stop()

if __name__ == "__main__":
    run_processing_pipeline()
