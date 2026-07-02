#!/usr/bin/env python3

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from pyspark.sql import SparkSession
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

env_path = ROOT_DIR / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

def create_spark_session():
    """Create simple Spark session"""
    spark = SparkSession.builder.appName(os.getenv("SPARK_APP_NAME")).getOrCreate()
    
    spark.sparkContext.setLogLevel("INFO")
    return spark

def main():
    try:
        logger.info("Creating Spark session...")
        spark = create_spark_session()
        
        logger.info("Testing basic Spark functionality...")
        # Test basic functionality
        df = spark.range(10)
        count = df.count()
        logger.info(f"Successfully created DataFrame with {count} rows")
        
        # Test file reading
        logger.info("Testing file reading...")
        try:
            # Try to read one of our source files
            json_df = spark.read.json("/home/belaid-abderrahim/Téléchargements/aws-marchespublics-annee-2022.json")
            json_df.head()
            logger.info(f"Successfully read JSON file with {json_df.count()} rows")
        except Exception as e:
            logger.warning(f"Could not read JSON file: {e}")
        
        spark.stop()
        logger.info("Spark test completed successfully!")
        
    except Exception as e:
        logger.error(f"Error in Spark test: {str(e)}")
        raise

if __name__ == "__main__":
    main()