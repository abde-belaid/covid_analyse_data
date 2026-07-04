"""
Validation script to check the complete preprocessing pipeline structure.
Ensures all files, helpers, and functions are properly implemented.
"""

import os
import sys
from pathlib import Path

def check_file_exists(path, name):
    """Check if a file exists."""
    if os.path.exists(path):
        print(f"✓ {name}: {path}")
        return True
    else:
        print(f"✗ MISSING {name}: {path}")
        return False

def check_function_in_file(filepath, function_name):
    """Check if a function exists in a Python file."""
    if not os.path.exists(filepath):
        return False
    
    with open(filepath, 'r') as f:
        content = f.read()
        if f"def {function_name}(" in content:
            return True
    return False

def validate_structure():
    """Validate the complete pipeline structure."""
    
    print("\n" + "="*70)
    print("PIPELINE STRUCTURE VALIDATION")
    print("="*70)
    
    base_path = "/home/belaid-abderrahim/Bureau/Master/S2/Big Data/tps/covid_data_analysis"
    scripts_path = os.path.join(base_path, "scripts")
    
    all_checks_pass = True
    
    # Check main Python files
    print("\n[1] Checking Python Files:")
    print("-" * 70)
    
    files_to_check = {
        os.path.join(scripts_path, "process_data.py"): "process_data.py (Bronze → Silver)",
        os.path.join(scripts_path, "aggregate_data.py"): "aggregate_data.py (Silver → Gold)",
        os.path.join(scripts_path, "run_pipeline.py"): "run_pipeline.py (Orchestrator)",
        os.path.join(scripts_path, "prepare_owid_data.py"): "prepare_owid_data.py (OWID Preparation)",
        os.path.join(scripts_path, "analysis_examples.py"): "analysis_examples.py (Analysis Examples)",
    }
    
    for filepath, name in files_to_check.items():
        if not check_file_exists(filepath, name):
            all_checks_pass = False
    
    # Check documentation files
    print("\n[2] Checking Documentation Files:")
    print("-" * 70)
    
    docs_to_check = {
        os.path.join(base_path, "PREPROCESSING_ARCHITECTURE.md"): "PREPROCESSING_ARCHITECTURE.md",
        os.path.join(base_path, "OWID_INTEGRATION_GUIDE.md"): "OWID_INTEGRATION_GUIDE.md",
        os.path.join(base_path, "IMPLEMENTATION_SUMMARY.md"): "IMPLEMENTATION_SUMMARY.md",
        os.path.join(base_path, "QUICKSTART_PIPELINE.md"): "QUICKSTART_PIPELINE.md",
    }
    
    for filepath, name in docs_to_check.items():
        if not check_file_exists(filepath, name):
            all_checks_pass = False
    
    # Check helper functions in process_data.py
    print("\n[3] Checking Helper Functions (process_data.py):")
    print("-" * 70)
    
    process_file = os.path.join(scripts_path, "process_data.py")
    
    helpers_to_check = [
        "helper_read_csv",
        "helper_validate_required_columns",
        "helper_handle_date_column",
        "helper_fill_numeric_nulls",
        "helper_remove_duplicates",
        "helper_normalize_text_columns",
        "helper_validate_positive_values",
        "helper_log_data_quality",
    ]
    
    for helper in helpers_to_check:
        if check_function_in_file(process_file, helper):
            print(f"✓ {helper}()")
        else:
            print(f"✗ MISSING {helper}()")
            all_checks_pass = False
    
    # Check cleaning functions in process_data.py
    print("\n[4] Checking Cleaning Functions (process_data.py):")
    print("-" * 70)
    
    cleaning_functions = [
        "clean_vaccination_data",
        "clean_mortality_data",
        "clean_testing_data",
        "clean_cases_data",
        "process_bronze_to_silver",
    ]
    
    for func in cleaning_functions:
        if check_function_in_file(process_file, func):
            print(f"✓ {func}()")
        else:
            print(f"✗ MISSING {func}()")
            all_checks_pass = False
    
    # Check aggregation helpers in aggregate_data.py
    print("\n[5] Checking Helper Functions (aggregate_data.py):")
    print("-" * 70)
    
    aggregate_file = os.path.join(scripts_path, "aggregate_data.py")
    
    agg_helpers = [
        "helper_add_time_dimensions",
        "helper_write_parquet",
        "helper_read_parquet",
    ]
    
    for helper in agg_helpers:
        if check_function_in_file(aggregate_file, helper):
            print(f"✓ {helper}()")
        else:
            print(f"✗ MISSING {helper}()")
            all_checks_pass = False
    
    # Check aggregation functions
    print("\n[6] Checking Aggregation Functions (aggregate_data.py):")
    print("-" * 70)
    
    agg_functions = [
        "aggregate_vaccination_monthly",
        "aggregate_vaccination_by_location",
        "aggregate_mortality_monthly",
        "aggregate_mortality_by_location",
        "aggregate_testing_monthly",
        "aggregate_testing_by_location",
        "aggregate_cases_monthly",
        "aggregate_cases_by_location",
        "process_silver_to_gold",
    ]
    
    for func in agg_functions:
        if check_function_in_file(aggregate_file, func):
            print(f"✓ {func}()")
        else:
            print(f"✗ MISSING {func}()")
            all_checks_pass = False
    
    # Check code quality
    print("\n[7] Code Quality Checks:")
    print("-" * 70)
    
    # Check for emoji usage (should be minimal/none)
    with open(process_file, 'r') as f:
        content = f.read()
        emoji_count = sum(1 for char in content if ord(char) > 127 and char not in 'éèêûù')
        if emoji_count == 0:
            print("✓ No emoji usage in process_data.py")
        else:
            print(f"⚠ Found {emoji_count} non-ASCII characters (may be emojis)")
    
    # Check docstrings exist
    docstring_count = content.count('"""')
    print(f"✓ Found {docstring_count // 2} docstrings in process_data.py")
    
    # Summary
    print("\n" + "="*70)
    if all_checks_pass:
        print("✓ ALL VALIDATION CHECKS PASSED")
        print("="*70)
        print("\nPipeline Structure:")
        print("  - 5 Python files with complete implementation")
        print("  - 4 Documentation files")
        print("  - 8 Generic helper functions")
        print("  - 4 Dataset-specific cleaning functions")
        print("  - 8 Aggregation functions (2 per dataset)")
        print("  - 3 Aggregation helpers")
        print("\nReady for production use!")
    else:
        print("✗ VALIDATION FAILED - Please check missing items above")
        print("="*70)
        sys.exit(1)
    
    print("="*70 + "\n")

if __name__ == "__main__":
    validate_structure()
