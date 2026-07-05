"""
Utility script to prepare OWID COVID-19 data for the pipeline.
Extracts specific columns into separate CSV files for each data type.

Usage:
    python scripts/prepare_owid_data.py --input data/bronze/owid-covid-data.csv
"""

import pandas as pd
import argparse
from pathlib import Path
import sys


def extract_vaccination_data(df, output_path):
    """
    Extract vaccination-related columns.
    """
    print("Extracting vaccination data...")
    
    vax_cols = [
        'iso_code', 'location', 'date',
        'total_vaccinations', 'people_vaccinated',
        'people_fully_vaccinated', 'people_boosted'
    ]
    
    # Filter columns that exist
    available_vax_cols = [col for col in vax_cols if col in df.columns]
    
    df_vax = df[available_vax_cols].copy()
    df_vax = df_vax.dropna(subset=['location', 'date'])
    df_vax = df_vax[df_vax['location'].notna() & (df_vax['location'] != '')]
    
    df_vax.to_csv(output_path, index=False)
    
    print(f"Saved {len(df_vax):,} vaccination records to {output_path}")
    print(f"Columns: {available_vax_cols}")
    return len(df_vax)


def extract_mortality_data(df, output_path):
    """
    Extract mortality-related columns.
    """
    print("Extracting mortality data...")
    
    mort_cols = [
        'iso_code', 'location', 'date',
        'total_deaths', 'new_deaths'
    ]
    
    # Filter columns that exist
    available_mort_cols = [col for col in mort_cols if col in df.columns]
    
    df_mort = df[available_mort_cols].copy()
    df_mort = df_mort.dropna(subset=['location', 'date'])
    df_mort = df_mort[df_mort['location'].notna() & (df_mort['location'] != '')]
    
    df_mort.to_csv(output_path, index=False)
    
    print(f"Saved {len(df_mort):,} mortality records to {output_path}")
    print(f"Columns: {available_mort_cols}")
    return len(df_mort)


def extract_testing_data(df, output_path):
    """
    Extract testing-related columns.
    """
    print("Extracting testing data...")
    
    test_cols = [
        'iso_code', 'location', 'date',
        'total_tests', 'new_tests', 'tests_per_case', 'positive_rate'
    ]
    
    # Filter columns that exist
    available_test_cols = [col for col in test_cols if col in df.columns]
    
    df_test = df[available_test_cols].copy()
    df_test = df_test.dropna(subset=['location', 'date'])
    df_test = df_test[df_test['location'].notna() & (df_test['location'] != '')]
    
    df_test.to_csv(output_path, index=False)
    
    print(f"Saved {len(df_test):,} testing records to {output_path}")
    print(f"Columns: {available_test_cols}")
    return len(df_test)


def extract_cases_data(df, output_path):
    """
    Extract cases-related columns.
    """
    print("Extracting cases data...")
    
    cases_cols = [
        'iso_code', 'location', 'date',
        'total_cases', 'new_cases'
    ]
    
    # Filter columns that exist
    available_cases_cols = [col for col in cases_cols if col in df.columns]
    
    df_cases = df[available_cases_cols].copy()
    df_cases = df_cases.dropna(subset=['location', 'date'])
    df_cases = df_cases[df_cases['location'].notna() & (df_cases['location'] != '')]
    
    df_cases.to_csv(output_path, index=False)
    
    print(f"Saved {len(df_cases):,} cases records to {output_path}")
    print(f"Columns: {available_cases_cols}")
    return len(df_cases)


def filter_by_country(input_csv, output_dir, country_name):
    """
    Extract data for a specific country only.
    """
    print(f"\nFiltering data for {country_name}...")
    
    df = pd.read_csv(input_csv)
    df_country = df[df['location'] == country_name]
    
    print(f"Found {len(df_country):,} records for {country_name}")
    
    # Create output files
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    extract_vaccination_data(df_country, f"{output_dir}/vaccination.csv")
    extract_mortality_data(df_country, f"{output_dir}/mortality.csv")
    extract_testing_data(df_country, f"{output_dir}/testing.csv")
    extract_cases_data(df_country, f"{output_dir}/cases.csv")


def prepare_all_data(input_csv, output_dir):
    """
    Extract all data types into separate files.
    """
    print(f"Reading data from {input_csv}...")
    df = pd.read_csv(input_csv)
    
    print(f"Total records in source: {len(df):,}")
    print(f"Available columns: {len(df.columns)}")
    print(f"Countries/regions: {df['location'].nunique()}")
    
    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    print("\n" + "="*70)
    print("EXTRACTING DATA BY TYPE")
    print("="*70)
    
    vax_count = extract_vaccination_data(df, f"{output_dir}/vaccination.csv")
    print()
    
    mort_count = extract_mortality_data(df, f"{output_dir}/mortality.csv")
    print()
    
    test_count = extract_testing_data(df, f"{output_dir}/testing.csv")
    print()
    
    cases_count = extract_cases_data(df, f"{output_dir}/cases.csv")
    
    print("\n" + "="*70)
    print("EXTRACTION SUMMARY")
    print("="*70)
    print(f"Vaccination records: {vax_count:,}")
    print(f"Mortality records:   {mort_count:,}")
    print(f"Testing records:     {test_count:,}")
    print(f"Cases records:       {cases_count:,}")
    print(f"Output directory:    {output_dir}")
    print("="*70 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Prepare OWID COVID-19 data for the pipeline"
    )
    
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Path to OWID COVID-19 CSV file (owid-covid-data.csv)"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        default="data/bronze",
        help="Output directory for split CSV files (default: data/bronze)"
    )
    
    parser.add_argument(
        "--country",
        type=str,
        default=None,
        help="Extract data for a specific country only (optional)"
    )
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not Path(args.input).exists():
        print(f"Error: Input file not found: {args.input}")
        sys.exit(1)
    
    print("\n" + "="*70)
    print("OWID COVID-19 DATA PREPARATION UTILITY")
    print("="*70)
    
    if args.country:
        filter_by_country(args.input, args.output, args.country)
    else:
        prepare_all_data(args.input, args.output)


if __name__ == "__main__":
    main()
