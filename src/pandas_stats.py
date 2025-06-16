#!/usr/bin/env python3
"""
pandas_stats.py

Compute descriptive statistics on 2024_fb_ads_president_scored_anon.csv using pandas.

Usage:
    python pandas_stats.py
"""

import pandas as pd
import json
import sys
from pathlib import Path


def get_csv_path():
    """Get CSV file path from user input or use default."""
    # Default path (update this to your actual file location)
    default_path = "C:/Users/sumuk/Downloads/2024_fb_ads_president_scored_anon.csv"
    
    print("CSV File Path Options:")
    print(f"1. Use default: {default_path}")
    print("2. Enter custom path")
    print("3. Enter just filename (if in current directory)")
    
    choice = input("\nEnter choice (1-3) or press Enter for default: ").strip()
    
    if choice == "2":
        csv_path = input("Enter full path to CSV file: ").strip()
    elif choice == "3":
        filename = input("Enter filename: ").strip()
        csv_path = Path.cwd() / filename
    else:
        csv_path = default_path
    
    return Path(csv_path)


def load_data(csv_path):
    """Load CSV data using pandas."""
    try:
        df = pd.read_csv(csv_path)
        print(f"Loaded {len(df)} rows with {len(df.columns)} columns")
        print(f"Columns: {list(df.columns)}")
        return df
    except FileNotFoundError:
        print(f"Error: File {csv_path} not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading CSV: {e}")
        sys.exit(1)


def detect_column_types(df):
    """Detect numeric and categorical columns using pandas dtypes."""
    # Get numeric columns (int, float)
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    
    # Get categorical columns (object, string, category)
    categorical_cols = df.select_dtypes(include=['object', 'string', 'category']).columns.tolist()
    
    print(f"Detected {len(numeric_cols)} numeric columns and {len(categorical_cols)} categorical columns")
    return numeric_cols, categorical_cols


def compute_numeric_stats_pandas(df, numeric_cols):
    """Compute descriptive statistics for numeric columns using pandas."""
    if not numeric_cols:
        return {}
    
    # Use DataFrame.describe() for comprehensive stats
    desc_stats = df[numeric_cols].describe()
    
    stats = {}
    for col in numeric_cols:
        # Convert pandas describe output to our format
        col_data = df[col].dropna()  # Remove NaN values
        
        if len(col_data) == 0:
            stats[col] = {
                'count': 0,
                'mean': None,
                'median': None,
                'min': None,
                'max': None,
                'std_dev': None
            }
        else:
            stats[col] = {
                'count': int(desc_stats.loc['count', col]),
                'mean': round(desc_stats.loc['mean', col], 4),
                'median': round(col_data.median(), 4),  # describe() uses 50% percentile
                'min': desc_stats.loc['min', col],
                'max': desc_stats.loc['max', col],
                'std_dev': round(desc_stats.loc['std', col], 4) if desc_stats.loc['count', col] > 1 else 0.0
            }
    
    return stats


def compute_categorical_stats_pandas(df, categorical_cols):
    """Compute descriptive statistics for categorical columns using pandas."""
    if not categorical_cols:
        return {}
    
    stats = {}
    for col in categorical_cols:
        # Remove empty/null values
        col_data = df[col].dropna()
        col_data = col_data[col_data.astype(str).str.strip() != '']
        
        if len(col_data) == 0:
            stats[col] = {
                'unique_values': 0,
                'mode': None,
                'mode_count': 0,
                'total_count': 0
            }
        else:
            # Use value_counts() and nunique()
            value_counts = col_data.value_counts()
            unique_count = col_data.nunique()
            
            # Get mode (most frequent value)
            mode_val = value_counts.index[0] if len(value_counts) > 0 else None
            mode_count = value_counts.iloc[0] if len(value_counts) > 0 else 0
            
            # Get top 5 values
            top_5 = value_counts.head(5).to_dict()
            
            stats[col] = {
                'unique_values': unique_count,
                'mode': mode_val,
                'mode_count': int(mode_count),
                'total_count': len(col_data),
                'top_5_values': top_5
            }
    
    return stats


def group_and_compute_pandas(df, group_keys, numeric_cols, categorical_cols):
    """Group data and compute stats using pandas groupby."""
    # Handle missing values in grouping columns
    df_grouped = df.copy()
    for key in group_keys:
        df_grouped[key] = df_grouped[key].fillna('NULL').astype(str)
    
    # Group by the specified keys
    grouped = df_grouped.groupby(group_keys)
    
    result = {}
    print(f"Computing stats for {len(grouped)} groups...")
    
    for group_name, group_df in grouped:
        # Convert group_name to tuple if it's not already
        if not isinstance(group_name, tuple):
            group_name = (group_name,)
        
        # Compute stats for this group
        numeric_stats = compute_numeric_stats_pandas(group_df, numeric_cols)
        categorical_stats = compute_categorical_stats_pandas(group_df, categorical_cols)
        
        result[group_name] = {
            'group_size': len(group_df),
            'numeric_stats': numeric_stats,
            'categorical_stats': categorical_stats
        }
    
    return result


def stringify_keys(d):
    """Convert tuple keys to pipe-delimited strings for JSON compatibility."""
    new = {}
    for k, v in d.items():
        if isinstance(k, tuple):
            new_key = '|'.join(map(str, k))
        else:
            new_key = str(k)
        new[new_key] = v
    return new


def save_json(data, filename):
    """Save data to JSON file with error handling."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        print(f"✓ Saved: {filename}")
    except Exception as e:
        print(f"Error saving {filename}: {e}")


def main():
    print("=" * 60)
    print("FACEBOOK ADS STATISTICS ANALYZER (PANDAS VERSION)")
    print("=" * 60)
    
    # Get CSV file path
    csv_path = get_csv_path()
    
    if not csv_path.exists():
        print(f"\n❌ Error: File {csv_path} does not exist")
        print("Please check the file path and try again.")
        sys.exit(1)

    # Get output filename
    output_name = input("\nEnter output filename base (or press Enter for 'pandas_stats_output'): ").strip()
    if not output_name:
        output_name = "pandas_stats_output"

    print(f"\n🔄 Processing: {csv_path}")
    
    # Load data with pandas
    df = load_data(csv_path)
    
    if df.empty:
        print("No data to process")
        sys.exit(1)

    # Detect column types
    numeric_cols, categorical_cols = detect_column_types(df)
    
    if not numeric_cols and not categorical_cols:
        print("No valid columns found")
        sys.exit(1)

    print("\n" + "="*50)
    print("COMPUTING OVERALL STATISTICS")
    print("="*50)
    
    # Overall stats using pandas methods
    overall = {
        'dataset_info': {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'numeric_columns': numeric_cols,
            'categorical_columns': categorical_cols,
            'memory_usage': f"{df.memory_usage().sum() / 1024:.2f} KB"
        },
        'numeric': compute_numeric_stats_pandas(df, numeric_cols),
        'categorical': compute_categorical_stats_pandas(df, categorical_cols)
    }
    
    save_json(overall, f'{output_name}_overall.json')

    # By page_id (if exists)
    if 'page_id' in df.columns:
        print("\n" + "="*50)
        print("COMPUTING STATS BY PAGE_ID")
        print("="*50)
        by_page = group_and_compute_pandas(df, ['page_id'], numeric_cols, categorical_cols)
        by_page = stringify_keys(by_page)
        save_json(by_page, f'{output_name}_by_page.json')

    # By page_id and ad_id (if both exist)
    if 'page_id' in df.columns and 'ad_id' in df.columns:
        print("\n" + "="*50)
        print("COMPUTING STATS BY PAGE_ID AND AD_ID")
        print("="*50)
        by_page_ad = group_and_compute_pandas(df, ['page_id', 'ad_id'], numeric_cols, categorical_cols)
        by_page_ad = stringify_keys(by_page_ad)
        save_json(by_page_ad, f'{output_name}_by_page_ad.json')

    print("\n✅ All statistics computed and saved successfully!")
    print("\n📊 Pandas Methods Used:")
    print("   • DataFrame.describe() - for comprehensive numeric statistics")
    print("   • value_counts() - for categorical frequency analysis")
    print("   • nunique() - for counting unique values")
    print("   • groupby() - for grouped analysis")
    print("   • select_dtypes() - for automatic column type detection")


if __name__ == '__main__':
    main()
