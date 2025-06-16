#!/usr/bin/env python3
"""
pandas_stats.py

Compute descriptive statistics on 2024_fb_ads_president_scored_anon.csv using pandas.

Usage:
    python pandas_stats.py /path/to/2024_fb_ads_president_scored_anon.csv --output stats_output
"""

import argparse
import json
import pandas as pd

def main():
    parser = argparse.ArgumentParser(description='Descriptive stats with pandas')
    parser.add_argument('csv_path', help='Path to CSV file')
    parser.add_argument('--output', help='Output basename for JSON files', default='stats_output')
    args = parser.parse_args()

    df = pd.read_csv(args.csv_path)
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = df.select_dtypes(exclude=['number']).columns.tolist()

    # Overall numeric stats
    overall_num = df[numeric_cols].agg(['count','mean','min','max','std']).to_dict()
    # Overall categorical stats
    overall_cat = {
        col: {
            'unique_values': int(df[col].nunique()),
            'mode': df[col].mode().iloc[0] if not df[col].mode().empty else None,
            'mode_count': int(df[col].value_counts().iloc[0]) if not df[col].value_counts().empty else 0
        }
        for col in categorical_cols
    }
    with open(f"{args.output}_overall.json", 'w') as f:
        json.dump({'numeric': overall_num, 'categorical': overall_cat}, f, indent=2)

    # Stats by page_id
    by_page = {}
    for page, group in df.groupby('page_id'):
        num = group[numeric_cols].agg(['count','mean','min','max','std']).to_dict()
        cat = {
            col: {
                'unique_values': int(group[col].nunique()),
                'mode': group[col].mode().iloc[0] if not group[col].mode().empty else None,
                'mode_count': int(group[col].value_counts().iloc[0]) if not group[col].value_counts().empty else 0
            }
            for col in categorical_cols
        }
        by_page[page] = {'numeric_stats': num, 'categorical_stats': cat}
    with open(f"{args.output}_by_page.json", 'w') as f:
        json.dump(by_page, f, indent=2)

    # Stats by page_id and ad_id
    by_page_ad = {}
    for (page, ad), group in df.groupby(['page_id','ad_id']):
        num = group[numeric_cols].agg(['count','mean','min','max','std']).to_dict()
        cat = {
            col: {
                'unique_values': int(group[col].nunique()),
                'mode': group[col].mode().iloc[0] if not group[col].mode().empty else None,
                'mode_count': int(group[col].value_counts().iloc[0]) if not group[col].value_counts().empty else 0
            }
            for col in categorical_cols
        }
        by_page_ad[f"{page}|{ad}"] = {'numeric_stats': num, 'categorical_stats': cat}
    with open(f"{args.output}_by_page_ad.json", 'w') as f:
        json.dump(by_page_ad, f, indent=2)

    print("[pandas] Stats written to JSON files.")

if __name__ == '__main__':
    main()
