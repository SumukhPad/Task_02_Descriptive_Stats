#!/usr/bin/env python3
"""
pure_python_stats.py

Compute descriptive statistics on 2024_fb_ads_president_scored_anon.csv using only Python stdlib.

Usage:
    python pure_python_stats.py /path/to/2024_fb_ads_president_scored_anon.csv
"""

import csv
import argparse
import statistics
import collections
import json


def load_rows(csv_path):
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = [row for row in reader]
    return rows


def detect_column_types(rows):
    if not rows:
        return [], []
    first_row = rows[0]
    numeric_cols = []
    categorical_cols = []
    for col in first_row:
        is_numeric = True
        for row in rows:
            try:
                float(row[col])
            except Exception:
                is_numeric = False
                break
        if is_numeric:
            numeric_cols.append(col)
        else:
            categorical_cols.append(col)
    return numeric_cols, categorical_cols


def compute_numeric_stats(rows, numeric_cols):
    stats = {}
    for col in numeric_cols:
        values = [float(row[col]) for row in rows]
        stats[col] = {
            'count': len(values),
            'mean': statistics.mean(values),
            'min': min(values),
            'max': max(values),
            'std_dev': statistics.stdev(values) if len(values) > 1 else 0.0
        }
    return stats


def compute_categorical_stats(rows, categorical_cols):
    stats = {}
    for col in categorical_cols:
        counter = collections.Counter(row[col] for row in rows)
        most_common, count = counter.most_common(1)[0]
        stats[col] = {
            'unique_values': len(counter),
            'mode': most_common,
            'mode_count': count
        }
    return stats


def group_and_compute(rows, key_cols, numeric_cols, categorical_cols):
    grouped = collections.defaultdict(list)
    for row in rows:
        key = tuple(row[k] for k in key_cols)
        grouped[key].append(row)
    group_stats = {}
    for key, group_rows in grouped.items():
        num_stats = compute_numeric_stats(group_rows, numeric_cols)
        cat_stats = compute_categorical_stats(group_rows, categorical_cols)
        group_stats[key] = {
            'numeric_stats': num_stats,
            'categorical_stats': cat_stats
        }
    return group_stats


def main():
    parser = argparse.ArgumentParser(description='Compute descriptive stats on FB ads data.')
    parser.add_argument('csv_path', help='Path to the CSV file')
    parser.add_argument('--output', help='Output JSON file basename', default='stats_output')
    args = parser.parse_args()

    rows = load_rows(args.csv_path)
    numeric_cols, categorical_cols = detect_column_types(rows)

    # Overall stats
    overall = {
        'numeric': compute_numeric_stats(rows, numeric_cols),
        'categorical': compute_categorical_stats(rows, categorical_cols)
    }
    with open(f'{args.output}_overall.json', 'w', encoding='utf-8') as f:
        json.dump(overall, f, indent=2)

    # Stats by page_id
    by_page = group_and_compute(rows, ['page_id'], numeric_cols, categorical_cols)
    with open(f'{args.output}_by_page.json', 'w', encoding='utf-8') as f:
        json.dump(by_page, f, indent=2)

    # Stats by page_id and ad_id
    by_page_ad = group_and_compute(rows, ['page_id', 'ad_id'], numeric_cols, categorical_cols)
    with open(f'{args.output}_by_page_ad.json', 'w', encoding='utf-8') as f:
        json.dump(by_page_ad, f, indent=2)

    print("Statistics computed and saved to JSON files.")


if __name__ == '__main__':
    main()
