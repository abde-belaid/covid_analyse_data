"""
Analysis examples using cleaned and aggregated COVID-19 data from Gold layer.
Shows how to leverage the fully processed datasets for insights.
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, max, min, avg, sum as spark_sum

from src.common.spark_config import create_spark_session

def example_1_vaccination_trends(spark):
    """
    Example 1: Analyze vaccination trends over time.
    Shows monthly vaccination progression by country.
    """
    print("\n" + "="*70)
    print("EXAMPLE 1: VACCINATION TRENDS OVER TIME")
    print("="*70)
    
    vax = spark.read.parquet("s3a://gold/vaccination_monthly/")
    
    # Top countries by fully vaccinated
    top_vax = vax.groupBy("location") \
        .agg(max("max_fully_vaccinated").alias("peak_fully_vaccinated")) \
        .orderBy(col("peak_fully_vaccinated").desc()) \
        .limit(10)
    
    print("\nTop 10 countries by peak fully vaccinated:")
    top_vax.show()
    
    return top_vax

def example_2_mortality_analysis(spark):
    """
    Example 2: Mortality statistics by country.
    Identifies countries with highest death tolls.
    """
    print("\n" + "="*70)
    print("EXAMPLE 2: MORTALITY STATISTICS")
    print("="*70)
    
    mort = spark.read.parquet("s3a://gold/mortality_by_location/")
    
    # Countries with highest mortality
    highest_deaths = mort.select(
        col("location"),
        col("total_deaths"),
        col("cumulative_new_deaths"),
        col("average_daily_deaths")
    ).orderBy(col("total_deaths").desc()).limit(15)
    
    print("\nCountries with highest total deaths:")
    highest_deaths.show()
    
    return highest_deaths

def example_3_testing_capacity(spark):
    """
    Example 3: Testing capacity analysis.
    Shows countries with highest testing volume.
    """
    print("\n" + "="*70)
    print("EXAMPLE 3: TESTING CAPACITY & POSITIVE RATES")
    print("="*70)
    
    test = spark.read.parquet("s3a://gold/testing_by_location/")
    
    # Countries with most tests
    top_testers = test.select(
        col("location"),
        col("total_tests"),
        col("average_positive_rate")
    ).orderBy(col("total_tests").desc()).limit(10)
    
    print("\nTop 10 countries by total tests:")
    top_testers.show()
    
    return top_testers

def example_4_correlation_vax_deaths(spark):
    """
    Example 4: Correlation between vaccination and deaths.
    Joins vaccination and mortality data for analysis.
    """
    print("\n" + "="*70)
    print("EXAMPLE 4: VACCINATION vs MORTALITY CORRELATION")
    print("="*70)
    
    vax = spark.read.parquet("s3a://gold/vaccination_monthly/")
    mort = spark.read.parquet("s3a://gold/mortality_monthly/")
    
    # Join on location, year, month
    combined = vax.join(
        mort,
        on=["location", "year", "month"],
        how="inner"
    )
    
    # Select relevant columns
    analysis = combined.select(
        col("location"),
        col("year"),
        col("month"),
        col("max_fully_vaccinated"),
        col("max_deaths"),
        col("avg_daily_deaths")
    ).orderBy("location", "year", "month")
    
    print("\nVaccination vs Mortality (sample rows):")
    analysis.limit(20).show()
    
    return analysis

def example_5_monthly_trends(spark, country="Morocco"):
    """
    Example 5: Monthly trends for a specific country.
    Detailed month-by-month analysis.
    """
    print("\n" + "="*70)
    print(f"EXAMPLE 5: DETAILED TRENDS FOR {country}")
    print("="*70)
    
    vax = spark.read.parquet("s3a://gold/vaccination_monthly/")
    mort = spark.read.parquet("s3a://gold/mortality_monthly/")
    cases = spark.read.parquet("s3a://gold/cases_monthly/")
    
    # Filter by country and join
    vax_country = vax.filter(col("location") == country)
    mort_country = mort.filter(col("location") == country)
    cases_country = cases.filter(col("location") == country)
    
    # Join all three datasets
    combined = vax_country \
        .join(mort_country, on=["year", "month"], how="left") \
        .join(cases_country, on=["year", "month"], how="left") \
        .select(
            col("year"),
            col("month"),
            col("max_fully_vaccinated"),
            col("max_deaths"),
            col("avg_daily_deaths"),
            col("max_cases"),
            col("avg_daily_cases")
        ).orderBy("year", "month")
    
    print(f"\nMonthly trends for {country}:")
    combined.show()
    
    return combined

def example_6_quarterly_summary(spark):
    """
    Example 6: Quarterly summary aggregation.
    High-level quarterly metrics across all regions.
    """
    print("\n" + "="*70)
    print("EXAMPLE 6: QUARTERLY SUMMARY")
    print("="*70)
    
    vax = spark.read.parquet("s3a://gold/vaccination_monthly/")
    
    # Quarterly aggregation
    quarterly = vax.withColumn("quarter", ((col("month") - 1) / 3).cast("int") + 1) \
        .groupBy("location", "year", "quarter") \
        .agg(
            max("max_fully_vaccinated").alias("quarterly_max_vax"),
            avg("avg_fully_vaccinated").alias("quarterly_avg_vax")
        ).orderBy("location", "year", "quarter")
    
    print("\nQuarterly vaccination summary:")
    quarterly.limit(20).show()
    
    return quarterly

def example_7_data_quality_stats(spark):
    """
    Example 7: Data quality and completeness statistics.
    Shows which countries have complete data coverage.
    """
    print("\n" + "="*70)
    print("EXAMPLE 7: DATA QUALITY & COMPLETENESS")
    print("="*70)
    
    vax = spark.read.parquet("s3a://gold/vaccination_by_location/")
    
    # Data completeness analysis
    quality = vax.select(
        col("location"),
        col("total_records"),
        col("first_vaccination_date"),
        col("last_vaccination_date")
    ).orderBy(col("total_records").desc())
    
    print("\nData completeness by location:")
    quality.limit(20).show()
    
    return quality

def main():
    """Run all analysis examples."""
    print("\n" + "="*70)
    print("COVID-19 DATA ANALYSIS EXAMPLES")
    print("Using cleaned and aggregated data from Gold layer")
    print("="*70)
    
    spark = create_spark_session()
    
    try:
        # Run examples
        example_1_vaccination_trends(spark)
        example_2_mortality_analysis(spark)
        example_3_testing_capacity(spark)
        example_4_correlation_vax_deaths(spark)
        example_5_monthly_trends(spark, country="Morocco")
        example_6_quarterly_summary(spark)
        example_7_data_quality_stats(spark)
        
        print("\n" + "="*70)
        print("All analysis examples completed successfully")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\nError running analysis: {e}")
        raise
    finally:
        spark.stop()

if __name__ == "__main__":
    main()
