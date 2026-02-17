"""
CSV Data Cleaner & Transformer
Removes duplicates, handles missing values, standardizes formatting
"""

import csv
import sys
from collections import Counter


def load_csv(filepath):
    """Load CSV file and return rows with headers"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            headers = reader.fieldnames
        return rows, headers
    except FileNotFoundError:
        print(f"❌ File not found: {filepath}")
        return None, None
    except Exception as e:
        print(f"❌ Error loading CSV: {e}")
        return None, None


def remove_duplicates(rows):
    """Remove duplicate rows based on all columns"""
    seen = set()
    unique_rows = []
    for row in rows:
        row_tuple = tuple(sorted(row.items()))
        if row_tuple not in seen:
            seen.add(row_tuple)
            unique_rows.append(row)
    return unique_rows


def handle_missing_values(rows, strategy='remove'):
    """Handle missing values: 'remove' or 'fill'"""
    if strategy == 'remove':
        return [row for row in rows if all(v.strip() for v in row.values())]
    elif strategy == 'fill':
        return [{k: v if v.strip() else 'N/A' for k, v in row.items()} for row in rows]
    return rows


def standardize_text(rows):
    """Standardize text: strip whitespace and title case"""
    for row in rows:
        for key, value in row.items():
            row[key] = str(value).strip().title() if isinstance(value, str) else value