#!/usr/bin/env python3
"""
polars_stats.py

Compute descriptive statistics on 2024_fb_ads_president_scored_anon.csv using Polars.

Usage:
    python polars_stats.py /path/to/2024_fb_ads_president_scored_anon.csv --output stats_output
"""

import argparse
import json
import polars as pl


def main():
    parser = argparse.ArgumentParser(description='Descriptive stats with Polars')
    parser.add_argument('csv_path', help='Path to CSV file')
    parser.add_argument('--output', help='Output basename for JSON files', default='stats_output')
    args = parser.parse_args()

    df = pl.read_csv(args.csv_path)
    # Identify numeric vs. categorical
    numeric_cols = [col for col, dtype in zip(df.columns, df.dtypes) if dtype in (pl.Int64, pl.Float64)]
    categorical_cols = [c for c in df.columns if c not in numeric_cols]

    # Overall numeric describe
    overall_num = df.select(numeric_cols).describe().to_dict()
    # Overall categorical counts/modes
    overall_cat = {}
    for col in categorical_cols:
        vc = df[col].value_counts()
        mode_row = vc[0]
        overall_cat[col] = {
            'unique_values': vc.height,
            'mode': mode_row['values'],
            'mode_count': int(mode_row['counts'])
        }

    # Save overall
    with open(f"{args.output}_overall.json", 'w') as f:
        json.dump({'numeric': overall_num, 'categorical': overall_cat}, f, indent=2)

    # Grouped stats helper
    def agg_group(group_df):
        num = group_df.select(numeric_cols).describe().to_dict()
        cat = {}
        for col in categorical_cols:
            vc = group_df[col].value_counts()
            if vc.height > 0:
                row = vc[0]
                cat[col] = {'unique_values': vc.height, 'mode': row['values'], 'mode_count': int(row['counts'])}
            else:
                cat[col] = {'unique_values': 0, 'mode': None, 'mode_count': 0}
        return num, cat

    # Stats by page_id
    by_page = {}
    for page, group_df in df.groupby('page_id'):
        num, cat = agg_group(group_df)
        by_page[page] = {'numeric_stats': num, 'categorical_stats': cat}
    with open(f"{args.output}_by_page.json", 'w') as f:
        json.dump(by_page, f, indent=2)

    # Stats by page_id and ad_id
    by_page_ad = {}
    for (page, ad), group_df in df.groupby(['page_id', 'ad_id']):
        num, cat = agg_group(group_df)
        by_page_ad[f"{page}|{ad}"] = {'numeric_stats': num, 'categorical_stats': cat}
    with open(f"{args.output}_by_page_ad.json", 'w') as f:
        json.dump(by_page_ad, f, indent=2)

    print("[polars] Stats written to JSON files.")

if __name__ == '__main__':
    main()
