import os
import sys
from pathlib import Path
from pyspark.sql.functions import (
    col, month, year, quarter, dayofyear, max as spark_max, 
    min as spark_min, avg, sum as spark_sum, count, stddev, percentile_approx, lit
)

from src.common.spark_config import create_spark_session
from src.common.utils import load_env

# ==================== HELPER FUNCTIONS FOR AGGREGATION ====================

def helper_add_time_dimensions(df):
    """
    Add time-based dimensions for temporal analysis.
    """
    return (
        df.withColumn("year", year(col("date")))
          .withColumn("month", month(col("date")))
          .withColumn("quarter", quarter(col("date")))
          .withColumn("day_of_year", dayofyear(col("date")))
    )

def helper_write_parquet(df, output_path, mode="overwrite"):
    """
    Write DataFrame to Parquet with error handling.
    """
    try:
        df.write.mode(mode).parquet(output_path)
        print(f"Successfully wrote {df.count()} records to {output_path}")
    except Exception as e:
        print(f"Error writing to {output_path}: {e}")
        raise

def helper_path_exists(spark, path):
    """
    Check whether a path exists in the configured Spark filesystem.
    """
    try:
        hadoop_path = spark._jvm.org.apache.hadoop.fs.Path(path)
        fs = hadoop_path.getFileSystem(spark._jsc.hadoopConfiguration())
        exists = fs.exists(hadoop_path)
        if not exists:
            print(f"Path not found: {path}")
        return exists
    except Exception as e:
        print(f"Unable to verify path existence for {path}: {e}")
        return False


def helper_read_parquet(spark, path):
    """
    Read Parquet file with error handling.
    """
    if not helper_path_exists(spark, path):
        print(f"Skipping missing input path: {path}")
        return None

    try:
        df = spark.read.parquet(path)
        print(f"Read {df.count()} records from {path}")
        return df
    except Exception as e:
        print(f"Error reading from {path}: {e}")
        raise

# ==================== VACCINATION AGGREGATIONS ====================

def aggregate_vaccination_monthly(spark, env):
    """
    Create monthly vaccination summary with comprehensive metrics.
    
    Args:
        spark (pyspark.sql.SparkSession): Active Spark session.
        env (dict): Environment variables.
        
    Returns:
        pyspark.sql.DataFrame: Aggregated monthly data.
    """
    print("\n--- Aggregating Vaccination Data (Monthly) ---")
    
    silver_bucket = env.get("MINIO_BUCKET_SILVER", "silver")
    gold_bucket = env.get("MINIO_BUCKET_GOLD", "gold")
    
    silver_path = f"s3a://{silver_bucket}/vaccination_cleaned"
    gold_path = f"s3a://{gold_bucket}/vaccination_monthly"
    
    df = helper_read_parquet(spark, silver_path)
    if df is None:
        return None
    
    df = helper_add_time_dimensions(df)

    aggregation_columns = [
        spark_max("total_vaccinations").alias("max_total_vaccinations"),
        spark_max("people_vaccinated").alias("max_people_vaccinated"),
        spark_max("people_fully_vaccinated").alias("max_fully_vaccinated"),
    ]
    if "people_boosted" in df.columns:
        aggregation_columns.append(spark_max("people_boosted").alias("max_boosted"))
    else:
        aggregation_columns.append(lit(0).alias("max_boosted"))

    aggregation_columns.extend([
        avg("total_vaccinations").alias("avg_total_vaccinations"),
        spark_min("total_vaccinations").alias("min_total_vaccinations"),
        count("*").alias("record_count")
    ])
    
    df_agg = (
        df.groupBy("location", "year", "month")
          .agg(*aggregation_columns)
          .orderBy("location", "year", "month")
    )
    
    helper_write_parquet(df_agg, gold_path)
    print(f"Vaccination monthly aggregation: {df_agg.count()} records")
    return df_agg

def aggregate_vaccination_by_location(spark, env):
    """
    Create overall vaccination summary by location (country-level).
    
    Args:
        spark (pyspark.sql.SparkSession): Active Spark session.
        env (dict): Environment variables.
        
    Returns:
        pyspark.sql.DataFrame: Aggregated data by location.
    """
    print("\n--- Aggregating Vaccination Data (By Location) ---")
    
    silver_bucket = env.get("MINIO_BUCKET_SILVER", "silver")
    gold_bucket = env.get("MINIO_BUCKET_GOLD", "gold")
    
    silver_path = f"s3a://{silver_bucket}/vaccination_cleaned"
    gold_path = f"s3a://{gold_bucket}/vaccination_by_location"
    
    df = helper_read_parquet(spark, silver_path)
    if df is None:
        return None
    
    # Location-level aggregation
    df_agg = (
        df.groupBy("location")
          .agg(
              spark_max("total_vaccinations").alias("max_total_vaccinations"),
              spark_max("people_fully_vaccinated").alias("max_fully_vaccinated"),
              spark_min("date").alias("first_vaccination_date"),
              spark_max("date").alias("last_vaccination_date"),
              count("*").alias("total_records")
          )
          .orderBy("location")
    )
    
    helper_write_parquet(df_agg, gold_path)
    print(f"Vaccination by location aggregation: {df_agg.count()} records")
    return df_agg

# ==================== MORTALITY AGGREGATIONS ====================

def aggregate_mortality_monthly(spark, env):
    """
    Create monthly mortality summary with statistical insights.
    """
    print("\n--- Aggregating Mortality Data (Monthly) ---")
    
    silver_bucket = env.get("MINIO_BUCKET_SILVER", "silver")
    gold_bucket = env.get("MINIO_BUCKET_GOLD", "gold")
    
    silver_path = f"s3a://{silver_bucket}/mortality_cleaned"
    gold_path = f"s3a://{gold_bucket}/mortality_monthly"
    
    df = helper_read_parquet(spark, silver_path)
    if df is None:
        return None
    
    # Add time dimensions
    df = helper_add_time_dimensions(df)
    
    # Monthly aggregation
    df_agg = (
        df.groupBy("location", "year", "month")
          .agg(
              spark_max("total_deaths").alias("max_deaths"),
              spark_sum("new_deaths").alias("total_new_deaths"),
              avg("new_deaths").alias("avg_daily_deaths"),
              spark_min("total_deaths").alias("min_deaths"),
              count("*").alias("record_count")
          )
          .orderBy("location", "year", "month")
    )
    
    helper_write_parquet(df_agg, gold_path)
    print(f"Mortality monthly aggregation: {df_agg.count()} records")
    return df_agg

def aggregate_mortality_by_location(spark, env):
    """
    Create overall mortality summary by location.
    """
    print("\n--- Aggregating Mortality Data (By Location) ---")
    
    silver_bucket = env.get("MINIO_BUCKET_SILVER", "silver")
    gold_bucket = env.get("MINIO_BUCKET_GOLD", "gold")
    
    silver_path = f"s3a://{silver_bucket}/mortality_cleaned"
    gold_path = f"s3a://{gold_bucket}/mortality_by_location"
    
    df = helper_read_parquet(spark, silver_path)
    if df is None:
        return None
    
    # Location-level aggregation
    df_agg = (
        df.groupBy("location")
          .agg(
              spark_max("total_deaths").alias("total_deaths"),
              spark_sum("new_deaths").alias("cumulative_new_deaths"),
              avg("new_deaths").alias("average_daily_deaths"),
              spark_min("date").alias("first_record_date"),
              spark_max("date").alias("last_record_date"),
              count("*").alias("total_records")
          )
          .orderBy("location")
    )
    
    helper_write_parquet(df_agg, gold_path)
    print(f"Mortality by location aggregation: {df_agg.count()} records")
    return df_agg

# ==================== TESTING AGGREGATIONS ====================

def aggregate_testing_monthly(spark, env):
    """
    Create monthly testing summary with testing statistics.
    """
    print("\n--- Aggregating Testing Data (Monthly) ---")
    
    silver_bucket = env.get("MINIO_BUCKET_SILVER", "silver")
    gold_bucket = env.get("MINIO_BUCKET_GOLD", "gold")
    
    silver_path = f"s3a://{silver_bucket}/testing_cleaned"
    gold_path = f"s3a://{gold_bucket}/testing_monthly"
    
    df = helper_read_parquet(spark, silver_path)
    if df is None:
        return None
    
    # Add time dimensions
    df = helper_add_time_dimensions(df)
    
    # Monthly aggregation
    df_agg = (
        df.groupBy("location", "year", "month")
          .agg(
              spark_max("total_tests").alias("max_tests"),
              spark_sum("new_tests").alias("total_new_tests"),
              avg("new_tests").alias("avg_daily_tests"),
              avg("positive_rate").alias("avg_positive_rate"),
              count("*").alias("record_count")
          )
          .orderBy("location", "year", "month")
    )
    
    helper_write_parquet(df_agg, gold_path)
    print(f"Testing monthly aggregation: {df_agg.count()} records")
    return df_agg

def aggregate_testing_by_location(spark, env):
    """
    Create overall testing summary by location.
    """
    print("\n--- Aggregating Testing Data (By Location) ---")
    
    silver_bucket = env.get("MINIO_BUCKET_SILVER", "silver")
    gold_bucket = env.get("MINIO_BUCKET_GOLD", "gold")
    
    silver_path = f"s3a://{silver_bucket}/testing_cleaned"
    gold_path = f"s3a://{gold_bucket}/testing_by_location"
    
    df = helper_read_parquet(spark, silver_path)
    if df is None:
        return None
    
    # Location-level aggregation
    df_agg = (
        df.groupBy("location")
          .agg(
              spark_max("total_tests").alias("total_tests"),
              spark_sum("new_tests").alias("cumulative_new_tests"),
              avg("positive_rate").alias("average_positive_rate"),
              spark_min("date").alias("first_record_date"),
              spark_max("date").alias("last_record_date"),
              count("*").alias("total_records")
          )
          .orderBy("location")
    )
    
    helper_write_parquet(df_agg, gold_path)
    print(f"Testing by location aggregation: {df_agg.count()} records")
    return df_agg

# ==================== CASES AGGREGATIONS ====================

def aggregate_cases_monthly(spark, env):
    """
    Create monthly cases summary with case statistics.
    """
    print("\n--- Aggregating Cases Data (Monthly) ---")
    
    silver_bucket = env.get("MINIO_BUCKET_SILVER", "silver")
    gold_bucket = env.get("MINIO_BUCKET_GOLD", "gold")
    
    silver_path = f"s3a://{silver_bucket}/cases_cleaned"
    gold_path = f"s3a://{gold_bucket}/cases_monthly"
    
    df = helper_read_parquet(spark, silver_path)
    if df is None:
        return None
    
    # Add time dimensions
    df = helper_add_time_dimensions(df)
    
    # Monthly aggregation
    df_agg = (
        df.groupBy("location", "year", "month")
          .agg(
              spark_max("total_cases").alias("max_cases"),
              spark_sum("new_cases").alias("total_new_cases"),
              avg("new_cases").alias("avg_daily_cases"),
              count("*").alias("record_count")
          )
          .orderBy("location", "year", "month")
    )
    
    helper_write_parquet(df_agg, gold_path)
    print(f"Cases monthly aggregation: {df_agg.count()} records")
    return df_agg

def aggregate_cases_by_location(spark, env):
    """
    Create overall cases summary by location.
    """
    print("\n--- Aggregating Cases Data (By Location) ---")
    
    silver_bucket = env.get("MINIO_BUCKET_SILVER", "silver")
    gold_bucket = env.get("MINIO_BUCKET_GOLD", "gold")
    
    silver_path = f"s3a://{silver_bucket}/cases_cleaned"
    gold_path = f"s3a://{gold_bucket}/cases_by_location"
    
    df = helper_read_parquet(spark, silver_path)
    if df is None:
        return None
    
    # Location-level aggregation
    df_agg = (
        df.groupBy("location")
          .agg(
              spark_max("total_cases").alias("total_cases"),
              spark_sum("new_cases").alias("cumulative_new_cases"),
              avg("new_cases").alias("average_daily_cases"),
              spark_min("date").alias("first_case_date"),
              spark_max("date").alias("last_record_date"),
              count("*").alias("total_records")
          )
          .orderBy("location")
    )
    
    helper_write_parquet(df_agg, gold_path)
    print(f"Cases by location aggregation: {df_agg.count()} records")
    return df_agg

# ==================== SILVER TO GOLD PIPELINE ====================

def process_silver_to_gold(spark, env):
    """
    Execute all aggregations from Silver to Gold layer.
    Transforms cleaned data into analysis-ready aggregates.
    """
    print("="*70)
    print("SILVER TO GOLD LAYER - DATA AGGREGATION")
    print("="*70)
    
    try:
        processed = []

        # Vaccination aggregations
        processed.append(aggregate_vaccination_monthly(spark, env) is not None)
        processed.append(aggregate_vaccination_by_location(spark, env) is not None)
        
        # Mortality aggregations
        processed.append(aggregate_mortality_monthly(spark, env) is not None)
        processed.append(aggregate_mortality_by_location(spark, env) is not None)
        
        # Testing aggregations
        processed.append(aggregate_testing_monthly(spark, env) is not None)
        processed.append(aggregate_testing_by_location(spark, env) is not None)
        
        # Cases aggregations
        processed.append(aggregate_cases_monthly(spark, env) is not None)
        processed.append(aggregate_cases_by_location(spark, env) is not None)

        if not any(processed):
            raise FileNotFoundError(
                "Aucune table Silver n'a été trouvée pour l'agrégation. Assurez-vous que le pipeline Bronze->Silver a produit des données."
            )
        
        print("\n" + "="*70)
        print("Silver to Gold aggregation completed successfully")
        print("All datasets ready for analysis")
        print("="*70)
        
    except Exception as e:
        print(f"Error in Silver to Gold pipeline: {e}")
        raise

def run_silver_to_gold_pipeline():
    """
    Execute the Silver to Gold aggregation pipeline.
    """
    env = load_env()
    print("Initializing Spark session for Silver to Gold processing...")
    spark = create_spark_session()
    
    try:
        process_silver_to_gold(spark, env)
        print("\nSilver to Gold processing completed successfully.")
    except Exception as e:
        print(f"Error in Silver to Gold pipeline: {e}")
        raise
    finally:
        spark.stop()
        print("Spark session closed.")

if __name__ == "__main__":
    run_silver_to_gold_pipeline()
