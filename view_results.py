"""
Simple viewer to preview the CSV output in the terminal
"""

import csv
import os
from typing import List, Dict


def load_csv(filename: str) -> List[Dict]:
    """Load CSV file and return as list of dictionaries"""
    if not os.path.exists(filename):
        return []
    
    data = []
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        data = list(reader)
    return data


def print_summary(data: List[Dict]):
    """Print summary statistics"""
    if not data:
        print("No data found.")
        return
    
    # Count by category
    categories = {}
    for row in data:
        cat = row.get('Category', 'Unknown')
        categories[cat] = categories.get(cat, 0) + 1
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total Markets: {len(data)}")
    print(f"\nBreakdown by Category:")
    for cat, count in sorted(categories.items()):
        print(f"  {cat:20s}: {count:4d} markets")
    print("="*60)


def print_top_performers(data: List[Dict], metric: str = 'Perf % 1M', limit: int = 10):
    """Print top performing markets by a specific metric"""
    if not data:
        return
    
    # Filter out N/A values and convert to float
    valid_data = []
    for row in data:
        value_str = row.get(metric, 'N/A')
        if value_str != 'N/A':
            try:
                value = float(value_str.replace('%', ''))
                valid_data.append((row, value))
            except ValueError:
                pass
    
    if not valid_data:
        print(f"\nNo valid data for {metric}")
        return
    
    # Sort by performance (descending)
    valid_data.sort(key=lambda x: x[1], reverse=True)
    
    print(f"\n{'='*80}")
    print(f"TOP {limit} PERFORMERS - {metric}")
    print(f"{'='*80}")
    print(f"{'Rank':<6} {'Symbol':<15} {'Name':<30} {metric}")
    print("-"*80)
    
    for idx, (row, value) in enumerate(valid_data[:limit], 1):
        symbol = row.get('Symbol', '')[:14]
        name = row.get('Name', '')[:29]
        print(f"{idx:<6} {symbol:<15} {name:<30} {value:>8.2f}%")


def print_worst_performers(data: List[Dict], metric: str = 'Perf % 1M', limit: int = 10):
    """Print worst performing markets by a specific metric"""
    if not data:
        return
    
    # Filter out N/A values and convert to float
    valid_data = []
    for row in data:
        value_str = row.get(metric, 'N/A')
        if value_str != 'N/A':
            try:
                value = float(value_str.replace('%', ''))
                valid_data.append((row, value))
            except ValueError:
                pass
    
    if not valid_data:
        return
    
    # Sort by performance (ascending)
    valid_data.sort(key=lambda x: x[1])
    
    print(f"\n{'='*80}")
    print(f"BOTTOM {limit} PERFORMERS - {metric}")
    print(f"{'='*80}")
    print(f"{'Rank':<6} {'Symbol':<15} {'Name':<30} {metric}")
    print("-"*80)
    
    for idx, (row, value) in enumerate(valid_data[:limit], 1):
        symbol = row.get('Symbol', '')[:14]
        name = row.get('Name', '')[:29]
        print(f"{idx:<6} {symbol:<15} {name:<30} {value:>8.2f}%")


def main():
    """Main viewer function"""
    filename = "capital_markets_analysis.csv"
    
    print("\n" + "="*60)
    print("Capital.com Markets Analysis Viewer")
    print("="*60)
    
    if not os.path.exists(filename):
        print(f"\n✗ File not found: {filename}")
        print("  Run 'python run_analyzer.py' first to generate the data.")
        return
    
    # Load data
    print(f"\nLoading {filename}...")
    data = load_csv(filename)
    
    if not data:
        print("✗ No data found in file")
        return
    
    print(f"✓ Loaded {len(data)} markets")
    
    # Print summary
    print_summary(data)
    
    # Print top/bottom performers for different time periods
    metrics = ['Perf % 1W', 'Perf % 1M', 'Perf % 1Y']
    
    for metric in metrics:
        print_top_performers(data, metric, limit=5)
        print_worst_performers(data, metric, limit=5)
    
    print("\n" + "="*60)
    print(f"Full data available in: {filename}")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
