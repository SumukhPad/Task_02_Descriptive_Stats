#!/usr/bin/env python3
"""
pure_python_stats.py

Compute descriptive statistics on 2024_fb_ads_president_scored_anon.csv using only Python stdlib.

Usage:
    python pure_python_stats.py /path/to/2024_fb_ads_president_scored_anon.csv
"""

import csv
import statistics
import collections
import json
import sys
from pathlib import Path


def load_rows(csv_path):
    """Load CSV data and return list of dictionaries."""
    try:
        with open(csv_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            if not rows:
                print(f"Warning: CSV file {csv_path} is empty")
                return []
            print(f"Loaded {len(rows)} rows with columns: {list(rows[0].keys())}")
            return rows
    except FileNotFoundError:
        print(f"Error: File {csv_path} not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading CSV: {e}")
        sys.exit(1)


def detect_column_types(rows):
    """Detect which columns are numeric vs categorical."""
    if not rows:
        return [], []
    
    numeric_cols, categorical_cols = [], []
    sample_size = min(100, len(rows))  # Check first 100 rows for efficiency
    
    for col in rows[0].keys():
        is_numeric = True
        non_empty_count = 0
        
        for i in range(sample_size):
            value = rows[i][col].strip()
            if value:  # Skip empty values
                non_empty_count += 1
                try:
                    # Try to convert to float
                    float(value)
                except (ValueError, TypeError):
                    is_numeric = False
                    break
        
        # Only consider numeric if we have non-empty values and they're all numeric
        if is_numeric and non_empty_count > 0:
            numeric_cols.append(col)
        else:
            categorical_cols.append(col)
    
    print(f"Detected {len(numeric_cols)} numeric columns and {len(categorical_cols)} categorical columns")
    return numeric_cols, categorical_cols


def compute_numeric_stats(rows, numeric_cols):
    """Compute descriptive statistics for numeric columns."""
    stats = {}
    for col in numeric_cols:
        # Filter out empty/invalid values
        vals = []
        for r in rows:
            try:
                val = r[col].strip()
                if val:  # Skip empty strings
                    vals.append(float(val))
            except (ValueError, TypeError):
                continue  # Skip invalid values
        
        if not vals:
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
                'count': len(vals),
                'mean': round(statistics.mean(vals), 4),
                'median': round(statistics.median(vals), 4),
                'min': min(vals),
                'max': max(vals),
                'std_dev': round(statistics.stdev(vals), 4) if len(vals) > 1 else 0.0
            }
    return stats


def compute_categorical_stats(rows, categorical_cols):
    """Compute descriptive statistics for categorical columns."""
    stats = {}
    for col in categorical_cols:
        # Count non-empty values
        values = [r[col].strip() for r in rows if r[col].strip()]
        
        if not values:
            stats[col] = {
                'unique_values': 0,
                'mode': None,
                'mode_count': 0,
                'total_count': 0
            }
        else:
            counter = collections.Counter(values)
            mode_val, mode_count = counter.most_common(1)[0]
            stats[col] = {
                'unique_values': len(counter),
                'mode': mode_val,
                'mode_count': mode_count,
                'total_count': len(values),
                'top_5_values': dict(counter.most_common(5))
            }
    return stats


def group_and_compute(rows, keys, numeric_cols, categorical_cols):
    """Group data by specified keys and compute stats for each group."""
    grouped = collections.defaultdict(list)
    
    for r in rows:
        # Create key tuple, handling missing values
        key_parts = []
        for k in keys:
            val = r.get(k, '').strip()
            key_parts.append(val if val else 'NULL')
        key = tuple(key_parts)
        grouped[key].append(r)
    
    result = {}
    print(f"Computing stats for {len(grouped)} groups...")
    
    for key, grp in grouped.items():
        result[key] = {
            'group_size': len(grp),
            'numeric_stats': compute_numeric_stats(grp, numeric_cols),
            'categorical_stats': compute_categorical_stats(grp, categorical_cols)
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
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✓ Saved: {filename}")
    except Exception as e:
        print(f"Error saving {filename}: {e}")


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


def main():
    print("=" * 60)
    print("FACEBOOK ADS STATISTICS ANALYZER")
    print("=" * 60)
    
    # Get CSV file path
    csv_path = get_csv_path()
    
    if not csv_path.exists():
        print(f"\n❌ Error: File {csv_path} does not exist")
        print("Please check the file path and try again.")
        sys.exit(1)

    # Get output filename
    output_name = input("\nEnter output filename base (or press Enter for 'stats_output'): ").strip()
    if not output_name:
        output_name = "stats_output"

    print(f"\n🔄 Processing: {csv_path}")
    rows = load_rows(csv_path)
    
    if not rows:
        print("No data to process")
        sys.exit(1)

    num_cols, cat_cols = detect_column_types(rows)
    
    if not num_cols and not cat_cols:
        print("No valid columns found")
        sys.exit(1)

    print("\n" + "="*50)
    print("COMPUTING OVERALL STATISTICS")
    print("="*50)
    
    # Overall stats
    overall = {
        'dataset_info': {
            'total_rows': len(rows),
            'numeric_columns': num_cols,
            'categorical_columns': cat_cols
        },
        'numeric': compute_numeric_stats(rows, num_cols),
        'categorical': compute_categorical_stats(rows, cat_cols)
    }
    save_json(overall, f'{output_name}_overall.json')

    # By page_id (if exists)
    if 'page_id' in rows[0]:
        print("\n" + "="*50)
        print("COMPUTING STATS BY PAGE_ID")
        print("="*50)
        by_page = group_and_compute(rows, ['page_id'], num_cols, cat_cols)
        by_page = stringify_keys(by_page)
        save_json(by_page, f'{output_name}_by_page.json')

    # By page_id and ad_id (if both exist)
    if 'page_id' in rows[0] and 'ad_id' in rows[0]:
        print("\n" + "="*50)
        print("COMPUTING STATS BY PAGE_ID AND AD_ID")
        print("="*50)
        by_page_ad = group_and_compute(rows, ['page_id', 'ad_id'], num_cols, cat_cols)
        by_page_ad = stringify_keys(by_page_ad)
        save_json(by_page_ad, f'{output_name}_by_page_ad.json')

    print("\n✅ All statistics computed and saved successfully!")


if __name__ == '__main__':
    main()
