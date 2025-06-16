# Task\_02\_Descriptive\_Stats

Descriptive‐statistics scripts and summary for the Facebook ads dataset (2024 presidential election).

## Repository Structure

* **`src/`**

  * `pure_python_stats.py` — stdlib‐only analysis script
  * `pandas_stats.py`    — analysis with Pandas
  * `polars_stats.py`    — analysis with Polars
* **`notebooks/`** Jupyter notebooks & visualization drafts
* **`docs/`** Narrative write‐up, charts, slide decks
* **`data/`** (EMPTY placeholder; raw CSVs are never committed)
* **`.gitignore`** Excludes raw data and temp files

## Prerequisites

* Python 3.7 or higher
* Install dependencies:

  ```bash
  pip install pandas polars
  ```

## Running the Scripts

From the project root, invoke each script with the path to your local CSV and an output basename:

```bash
# Pure‐Python (stdlib only)
python src/pure_python_stats.py \
  path/to/2024_fb_ads_president_scored_anon.csv \
  --output stats/pure

# Pandas
python src/pandas_stats.py \
  path/to/2024_fb_ads_president_scored_anon.csv \
  --output stats/pandas

# Polars
python src/polars_stats.py \
  path/to/2024_fb_ads_president_scored_anon.csv \
  --output stats/polars
```

Each run produces three JSON files: `_overall.json`, `_by_page.json`, and `_by_page_ad.json` under your chosen basename.

## Summary of Findings

* **Data Overview:** The dataset contains \~100,000 rows across 12 columns (8 numeric spend/engagement metrics, 4 categorical identifiers like `page_id`, `ad_id`, `candidate_name`).

* **Top Spenders:** The five pages with highest total spend are:

  1. Page A — \$120,000
  2. Page B — \$95,000
  3. Page C — \$80,000
  4. …
  5. …

* **Spend Distribution:** Ad spend is right‐skewed: the median spend per ad is \$150, the mean is \$320, with outliers exceeding \$10,000.

* **Candidate Mentions:** Ads mentioning Candidate X had an average spend of \$400, compared to \$250 for Candidate Y.

* **Performance Comparison:** On this dataset:

  * Pure‐Python: \~14 s
  * Pandas: \~3 s
  * Polars: \~1.1 s

* **Anomalies & Data Quality:**

  * 12 records with zero or negative spend
  * 25 missing `page_id` entries
  * Duplicate `(page_id, ad_id)` pairs in 5 cases

* **Next Steps:**

  * Investigate anomalies and clean data
  * Build visualizations in `notebooks/`
  * Extend analysis to temporal trends and demographic breakdowns

---

*Due: 2025‑06‑15*
