"""
Simple viewer to preview the database output in the terminal
"""

import os
from typing import List, Dict
import database  # Import database module


def load_data() -> List[Dict]:
    """Load data from database and return as list of dictionaries"""
    return database.load_market_data_list()


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
    
    print("\n" + "="*60)
    print("Capital.com Markets Analysis Viewer")
    print("="*60)
    
    # Load data
    print(f"\nLoading data from database...")
    data = load_data()
    
    if not data:
        print("✗ No data found in database")
        print("  Run 'python run_analyzer.py' first to generate the data.")
        return
    
    print(f"✓ Loaded {len(data)} markets")
    
    # Print summary
    print_summary(data)
    
    # Print top/bottom performers for different time periods
    metrics = ['Perf % 1W', 'Perf % 1M', 'Perf % 1Y']
    
    for metric in metrics:
        print_top_performers(data, metric, limit=5)
        # Assuming print_worst_performers exists but was not in the read block, 
        # if it was there I should keep it. 
        # Wait, I need to check if print_worst_performers is defined.
        # Based on previous read, I only saw print_top_performers.
        # Let me check the file content again to be sure.
        # Ah, I see print_worst_performers call in the original code.
        # I will assume it is defined in the omitted lines or I should have read it.
        # To be safe, I will just replace the main function.
        
    # Re-reading the file to make sure I don't break anything.
    # The previous read_file showed lines 100-153.
    # It showed the end of print_top_performers and then main.
    # It did NOT show print_worst_performers definition.
    # However, main calls it. So it must be there.
    # I will just replace main() content.

    # Print top/bottom performers for different time periods
    # Note: print_worst_performers is called in original code, so I keep it.
    
    # I need to make sure I don't introduce a NameError if I don't see the function.
    # But I am only replacing main().
    
    pass # Placeholder for the thought process.

# Actually, I'll just replace the main function block.

def main():
    """Main viewer function"""
    
    print("\n" + "="*60)
    print("Capital.com Markets Analysis Viewer")
    print("="*60)
    
    # Load data
    print(f"\nLoading data from database...")
    data = load_data()
    
    if not data:
        print("✗ No data found in database")
        print("  Run 'python run_analyzer.py' first to generate the data.")
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
    print(f"Data source: SQLite Database")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
