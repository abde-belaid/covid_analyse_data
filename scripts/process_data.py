import os
import sys
from pathlib import Path
from pyspark.sql.functions import (
    col, trim, upper, to_date, isnan, isnull, when, coalesce,
    count, sum as spark_sum, avg, min as spark_min, max as spark_max, lit
)
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, DateType

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.spark.spark_config import create_spark_session
from scripts.utils import load_env

# ==================== GENERIC HELPER FUNCTIONS ====================

def helper_read_csv(spark, path, schema=None):
    """
    Read CSV file with proper error handling and inference.
    """
    try:
        if schema:
            df = spark.read.schema(schema).csv(path, header=True, enforceSchema=True)
        else:
            df = spark.read.csv(path, header=True, inferSchema=True)
        return df
    except Exception as e:
        print(f"Error reading CSV from {path}: {e}")
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


def helper_validate_required_columns(df, required_cols):
    """
    Validate that all required columns exist in DataFrame.
    """
    missing_cols = set(required_cols) - set(df.columns)
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    print(f"All required columns present: {required_cols}")
    return True

def helper_handle_date_column(df, date_col="date"):
    """
    Convert date column to proper date type and filter nulls.
    """
    df = df.withColumn(date_col, to_date(col(date_col), "yyyy-MM-dd"))
    initial_count = df.count()
    df = df.filter(col(date_col).isNotNull())
    removed_count = initial_count - df.count()
    if removed_count > 0:
        print(f"Removed {removed_count} rows with null dates")
    return df

def helper_fill_numeric_nulls(df, numeric_cols, fill_value=0):
    """
    Fill null values in numeric columns with specified value.
    Only processes columns that exist in DataFrame.
    """
    existing_cols = [c for c in numeric_cols if c in df.columns]
    if existing_cols:
        df = df.fillna(fill_value, subset=existing_cols)
        print(f"Filled nulls in {existing_cols} with {fill_value}")
    return df


def helper_add_optional_column(df, column_name, fill_value=0):
    """
    Add a column if it is missing so downstream logic remains robust.
    """
    if column_name not in df.columns:
        df = df.withColumn(column_name, lit(fill_value))
    return df

def helper_remove_duplicates(df, subset=None):
    """
    Remove duplicate rows. If subset provided, deduplicate on those columns.
    """
    initial_count = df.count()
    if subset:
        df = df.dropDuplicates(subset=subset)
    else:
        df = df.dropDuplicates()
    final_count = df.count()
    removed = initial_count - final_count
    if removed > 0:
        print(f"Removed {removed} duplicate rows")
    return df

def helper_normalize_text_columns(df, text_cols):
    """
    Normalize text columns: trim whitespace and uppercase.
    """
    for col_name in text_cols:
        if col_name in df.columns:
            df = df.withColumn(col_name, trim(upper(col(col_name))))
    return df

def helper_validate_positive_values(df, numeric_cols):
    """
    Filter out rows with negative values in numeric columns.
    """
    initial_count = df.count()
    for col_name in numeric_cols:
        if col_name in df.columns:
            df = df.filter(col(col_name) >= 0)
    final_count = df.count()
    removed = initial_count - final_count
    if removed > 0:
        print(f"Removed {removed} rows with negative numeric values")
    return df

def helper_log_data_quality(df, dataset_name):
    """
    Log data quality statistics.
    """
    print(f"\nData Quality Report for {dataset_name}:")
    print(f"Total records: {df.count()}")
    print(f"Total columns: {len(df.columns)}")
    df.printSchema()

# ==================== VACCINATION DATA PROCESSING ====================

def clean_vaccination_data(df):
    """
    Rigorous cleaning of vaccination data with proper validation and deduplication.
    Expected columns: iso_code, location, date, total_vaccinations, 
                      people_vaccinated, people_fully_vaccinated, people_boosted
    """
    print("\n--- Processing Vaccination Data ---")
    
    # Validate required columns
    required_cols = ["location", "date"]
    helper_validate_required_columns(df, required_cols)
    
    # Normalize text columns
    text_cols = ["location", "iso_code"]
    df = helper_normalize_text_columns(df, text_cols)
    
    # Handle date column
    df = helper_handle_date_column(df, "date")
    
    # Remove duplicates based on location and date
    df = helper_remove_duplicates(df, subset=["location", "date"])
    
    # Fill numeric nulls with 0
    vaccination_cols = [
        "total_vaccinations", "people_vaccinated", 
        "people_fully_vaccinated", "people_boosted"
    ]
    df = helper_fill_numeric_nulls(df, vaccination_cols, fill_value=0)
    if "people_boosted" not in df.columns:
        df = df.withColumn("people_boosted", lit(0))
    
    # Validate positive values
    df = helper_validate_positive_values(df, vaccination_cols)
    
    # Sort for consistency
    df = df.orderBy("location", "date")
    
    helper_log_data_quality(df, "Vaccination Data")
    return df

# ==================== MORTALITY DATA PROCESSING ====================

def clean_mortality_data(df):
    """
    Rigorous cleaning of mortality data with proper validation and deduplication.
    Expected columns: iso_code, location, date, total_deaths, new_deaths
    """
    print("\n--- Processing Mortality Data ---")
    
    # Validate required columns
    required_cols = ["location", "date"]
    helper_validate_required_columns(df, required_cols)
    
    # Normalize text columns
    text_cols = ["location", "iso_code"]
    df = helper_normalize_text_columns(df, text_cols)
    
    # Handle date column
    df = helper_handle_date_column(df, "date")
    
    # Remove duplicates based on location and date
    df = helper_remove_duplicates(df, subset=["location", "date"])
    
    # Fill numeric nulls with 0
    mortality_cols = ["total_deaths", "new_deaths"]
    df = helper_fill_numeric_nulls(df, mortality_cols, fill_value=0)
    
    # Validate positive values
    df = helper_validate_positive_values(df, mortality_cols)
    
    # Sort for consistency
    df = df.orderBy("location", "date")
    
    helper_log_data_quality(df, "Mortality Data")
    return df

# ==================== TESTING DATA PROCESSING ====================

def clean_testing_data(df):
    """
    Rigorous cleaning of testing data with proper validation and deduplication.
    Expected columns: iso_code, location, date, total_tests, new_tests
    """
    print("\n--- Processing Testing Data ---")
    
    # Validate required columns
    required_cols = ["location", "date"]
    helper_validate_required_columns(df, required_cols)
    
    # Normalize text columns
    text_cols = ["location", "iso_code"]
    df = helper_normalize_text_columns(df, text_cols)
    
    # Handle date column
    df = helper_handle_date_column(df, "date")
    
    # Remove duplicates based on location and date
    df = helper_remove_duplicates(df, subset=["location", "date"])
    
    # Fill numeric nulls with 0
    testing_cols = ["total_tests", "new_tests", "tests_per_case", "positive_rate"]
    df = helper_fill_numeric_nulls(df, testing_cols, fill_value=0)
    
    # Validate positive values
    df = helper_validate_positive_values(df, testing_cols)
    
    # Sort for consistency
    df = df.orderBy("location", "date")
    
    helper_log_data_quality(df, "Testing Data")
    return df

# ==================== CASES DATA PROCESSING ====================

def clean_cases_data(df):
    """
    Rigorous cleaning of cases data with proper validation and deduplication.
    Expected columns: iso_code, location, date, total_cases, new_cases
    """
    print("\n--- Processing Cases Data ---")
    
    # Validate required columns
    required_cols = ["location", "date"]
    helper_validate_required_columns(df, required_cols)
    
    # Normalize text columns
    text_cols = ["location", "iso_code"]
    df = helper_normalize_text_columns(df, text_cols)
    
    # Handle date column
    df = helper_handle_date_column(df, "date")
    
    # Remove duplicates based on location and date
    df = helper_remove_duplicates(df, subset=["location", "date"])
    
    # Fill numeric nulls with 0
    cases_cols = ["total_cases", "new_cases"]
    df = helper_fill_numeric_nulls(df, cases_cols, fill_value=0)
    
    # Validate positive values
    df = helper_validate_positive_values(df, cases_cols)
    
    # Sort for consistency
    df = df.orderBy("location", "date")
    
    helper_log_data_quality(df, "Cases Data")
    return df

# ==================== BRONZE TO SILVER PIPELINE ====================

def process_bronze_to_silver(spark, env):
    """
    Read multiple COVID-19 data files from Bronze bucket, clean each with specific functions,
    and write cleaned datasets to Silver bucket in Parquet format.
    This layer handles: validation, deduplication, type conversion, and basic quality checks.
    """
    bronze_bucket = env.get("MINIO_BUCKET_BRONZE", "bronze")
    silver_bucket = env.get("MINIO_BUCKET_SILVER", "silver")
    
    print("="*70)
    print("BRONZE TO SILVER LAYER - DATA CLEANING AND VALIDATION")
    print("="*70)
    
    # Define file mappings: (input_file, output_path, cleaning_function)
    file_mappings = [
        (
            f"s3a://{bronze_bucket}/vaccination.csv",
            f"s3a://{silver_bucket}/vaccination_cleaned",
            clean_vaccination_data
        ),
        (
            f"s3a://{bronze_bucket}/mortality.csv",
            f"s3a://{silver_bucket}/mortality_cleaned",
            clean_mortality_data
        ),
        (
            f"s3a://{bronze_bucket}/testing.csv",
            f"s3a://{silver_bucket}/testing_cleaned",
            clean_testing_data
        ),
        (
            f"s3a://{bronze_bucket}/cases.csv",
            f"s3a://{silver_bucket}/cases_cleaned",
            clean_cases_data
        ),
    ]
    
    cleaned_datasets = {}
    
    for input_path, output_path, clean_func in file_mappings:
        try:
            print(f"\nProcessing {input_path}...")
            
            if not helper_path_exists(spark, input_path):
                print(f"Skipping missing Bronze dataset: {input_path}")
                continue

            # Read raw data
            df = helper_read_csv(spark, input_path)
            initial_count = df.count()
            print(f"Initial record count: {initial_count}")
            
            # Apply specific cleaning function
            df_cleaned = clean_func(df)
            final_count = df_cleaned.count()
            print(f"Final record count: {final_count}")
            print(f"Reduction: {((initial_count - final_count) / initial_count * 100):.2f}%")
            
            # Write to Silver layer
            print(f"Writing to {output_path}...")
            df_cleaned.write.mode("overwrite").parquet(output_path)
            
            cleaned_datasets[output_path.split("/")[-1]] = df_cleaned
            print(f"Successfully processed {output_path}")
            
        except Exception as e:
            print(f"Error processing {input_path}: {e}")
            raise
    
    if not cleaned_datasets:
        raise FileNotFoundError(
            "Aucun dataset Bronze valide n'a été trouvé. Vérifiez que les fichiers CSV existent dans le bucket Bronze."
        )

    print("\n" + "="*70)
    print(f"Processed {len(cleaned_datasets)} datasets to Silver layer")
    print("="*70)
    
    return cleaned_datasets

from scripts.aggregate_data import run_silver_to_gold_pipeline


def run_bronze_to_silver_pipeline():
    """
    Execute Bronze to Silver transformation pipeline.
    """
    env = load_env()
    print("Initializing Spark session for Bronze to Silver processing...")
    spark = create_spark_session()
    
    try:
        cleaned_datasets = process_bronze_to_silver(spark, env)
        print("\nBronze to Silver processing completed successfully.")
        return cleaned_datasets
    except Exception as e:
        print(f"Error in Bronze to Silver pipeline: {e}")
        raise
    finally:
        spark.stop()
        print("Spark session closed.")


def run_processing_pipeline():
    """
    Execute the full Bronze->Silver->Gold processing pipeline.
    """
    run_bronze_to_silver_pipeline()
    run_silver_to_gold_pipeline()


if __name__ == "__main__":
    run_processing_pipeline()
