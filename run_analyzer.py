"""
Main script to fetch and analyze Capital.com markets
Stores data directly to SQLite database (primary storage)
"""

import csv
import sqlite3
import time
import webbrowser
import threading
import subprocess
from datetime import datetime
from capital_analyzer import CapitalAPI
import os
import sys

# Import configuration
try:
    import config
except ImportError:
    print("[ERROR] config.py not found!")
    print("Please copy config_template.py to config.py and fill in your credentials.")
    sys.exit(1)


def format_percentage(value: float) -> str:
    """Format percentage value for display"""
    if value is None:
        return "N/A"
    return f"{value:.2f}%"


def init_database(db_path: str = 'market_data.db'):
    """Initialize SQLite database with markets table"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS markets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            symbol TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            current_price REAL,
            currency TEXT,
            price_change_pct REAL,
            perf_1w_pct REAL,
            perf_1m_pct REAL,
            perf_3m_pct REAL,
            perf_6m_pct REAL,
            perf_ytd_pct REAL,
            perf_1y_pct REAL,
            perf_5y_pct REAL,
            perf_10y_pct REAL,
            market_status TEXT,
            type TEXT,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS metadata (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"[OK] Database initialized at {db_path}")


def store_to_database(market_data: list, db_path: str = 'market_data.db'):
    """Store market data directly to SQLite database"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Clear existing data
        cursor.execute('DELETE FROM markets')
        
        # Parse percentage value
        def parse_pct(val):
            if val is None or val == 'N/A':
                return None
            if isinstance(val, str):
                try:
                    return float(val.replace('%', '').strip())
                except (ValueError, AttributeError):
                    return None
            return float(val)
        
        # Insert market data
        for row in market_data:
            cursor.execute('''
                INSERT INTO markets (
                    category, symbol, name, current_price, currency,
                    price_change_pct, perf_1w_pct, perf_1m_pct, perf_3m_pct,
                    perf_6m_pct, perf_ytd_pct, perf_1y_pct, perf_5y_pct,
                    perf_10y_pct, market_status, type
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                row.get('Category', ''),
                row.get('Symbol', ''),
                row.get('Name', ''),
                parse_pct(row.get('Current Price')),
                row.get('Currency', ''),
                parse_pct(row.get('Price Change %')),
                parse_pct(row.get('Perf % 1W')),
                parse_pct(row.get('Perf % 1M')),
                parse_pct(row.get('Perf % 3M')),
                parse_pct(row.get('Perf % 6M')),
                parse_pct(row.get('Perf % YTD')),
                parse_pct(row.get('Perf % 1Y')),
                parse_pct(row.get('Perf % 5Y')),
                parse_pct(row.get('Perf % 10Y')),
                row.get('Market Status', ''),
                row.get('Type', '')
            ))
        
        # Update metadata with last fetch time
        cursor.execute('DELETE FROM metadata WHERE key = ?', ('last_fetch_time',))
        cursor.execute(
            'INSERT INTO metadata (key, value) VALUES (?, ?)',
            ('last_fetch_time', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        )
        
        conn.commit()
        print(f"[OK] Stored {len(market_data)} markets to database")
        
    except Exception as e:
        print(f"[ERROR] Error storing to database: {e}")
        conn.rollback()
    finally:
        conn.close()


def fetch_and_analyze_markets(api: CapitalAPI, categories: list) -> list:
    """
    Fetch all markets and calculate performance metrics
    
    Returns:
        List of dictionaries with market data and performance metrics
    """
    # Category-specific limits
    CATEGORY_LIMITS = {
        'forex': 20,
        'commodities': 20,
        'shares': 20,
        'indices': 20,
        'etf': 20,
        'cryptocurrencies': 20,
    }
    
    all_data = []
    total_markets = 0
    
    for category in categories:
        print(f"\n{'='*60}")
        print(f"Processing category: {category.upper()}")
        print(f"{'='*60}")
        
        # Fetch markets in this category
        markets = api.get_markets_by_category(category)
        
        # Apply category-specific limit
        category_lower = category.lower()
        limit = CATEGORY_LIMITS.get(category_lower)
        if limit is not None:
            markets = markets[:limit]
            print(f"  Limiting to top {limit} {category} entries")
        
        for idx, market in enumerate(markets, 1):
            epic = market.get('epic')
            name = market.get('instrumentName', epic)
            
            print(f"  [{idx}/{len(markets)}] Processing {name} ({epic})...")
            
            # Get market details
            details = api.get_market_details(epic)
            
            if not details:
                print(f"    ⚠ Could not fetch details for {epic}")
                continue
            
            snapshot = details.get('snapshot', {})
            instrument = details.get('instrument', {})
            
            # Calculate performance metrics
            performance = api.calculate_performance(epic)
            
            # Compile data
            market_data = {
                'Category': category.title(),
                'Symbol': epic,
                'Name': name,
                'Current Price': snapshot.get('bid', 'N/A'),
                'Currency': instrument.get('currency', 'N/A'),
                'Price Change %': format_percentage(snapshot.get('percentageChange')),
                'Perf % 30M': format_percentage(performance.get('perf_30m')),
                'Perf % 1H': format_percentage(performance.get('perf_1h')),
                'Perf % 4H': format_percentage(performance.get('perf_4h')),
                'Perf % 6H': format_percentage(performance.get('perf_6h')),
                'Perf % 1D': format_percentage(performance.get('perf_1d')),
                'Perf % 1W': format_percentage(performance.get('perf_1w')),
                'Perf % 1M': format_percentage(performance.get('perf_1m')),
                'Perf % 3M': format_percentage(performance.get('perf_3m')),
                'Perf % 6M': format_percentage(performance.get('perf_6m')),
                'Perf % YTD': format_percentage(performance.get('perf_ytd')),
                'Perf % 1Y': format_percentage(performance.get('perf_1y')),
                'Perf % 5Y': format_percentage(performance.get('perf_5y')),
                'Perf % 10Y': format_percentage(performance.get('perf_10y')),
                'Market Status': snapshot.get('marketStatus', 'N/A'),
                'Type': instrument.get('type', category.upper()),
            }
            
            all_data.append(market_data)
            total_markets += 1
            
            # Rate limiting
            time.sleep(getattr(config, 'REQUEST_DELAY', 0.15))
            
            # Ping session every 20 requests to keep it alive
            if idx % 20 == 0:
                api.ping()
    
    print(f"\n{'='*60}")
    print(f"[OK] Completed! Processed {total_markets} markets across {len(categories)} categories")
    print(f"{'='*60}\n")
    
    return all_data


def export_to_csv(data: list, filename: str):
    """Export market data to CSV file"""
    if not data:
        print("[ERROR] No data to export")
        return
    
    # Define column order
    fieldnames = [
        'Category',
        'Symbol',
        'Name',
        'Current Price',
        'Currency',
        'Price Change %',
        'Perf % 30M',
        'Perf % 1H',
        'Perf % 4H',
        'Perf % 6H',
        'Perf % 1D',
        'Perf % 1W',
        'Perf % 1M',
        'Perf % 3M',
        'Perf % 6M',
        'Perf % YTD',
        'Perf % 1Y',
        'Perf % 5Y',
        'Perf % 10Y',
        'Market Status',
        'Type',
    ]
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        
        print(f"[OK] Data exported to: {filename}")
        print(f"  Total rows: {len(data)}")
    except Exception as e:
        print(f"[ERROR] Error exporting to CSV: {str(e)}")


def main():
    """Main execution function"""
    print("="*60)
    print("Capital.com Market Analyzer")
    print("="*60)
    print(f"Environment: {'DEMO' if config.USE_DEMO else 'LIVE'}")
    print(f"Categories: {', '.join(config.CATEGORIES)}")
    print(f"Database: market_data.db (primary storage)")
    print("="*60)
    
    # Initialize database
    print("\nInitializing SQLite database...")
    init_database('market_data.db')
    
    # Initialize API client
    print("Initializing API client...")
    api = CapitalAPI(
        api_key=config.API_KEY,
        identifier=config.USERNAME,
        password=config.PASSWORD,
        demo=config.USE_DEMO
    )
    
    # Create session
    if not api.create_session():
        print("[ERROR] Failed to create session. Please check your credentials.")
        return
    
    # Fetch and analyze markets
    start_time = datetime.now()
    market_data = fetch_and_analyze_markets(api, config.CATEGORIES)
    end_time = datetime.now()
    
    # Store to database (primary storage)
    if market_data:
        print("\nStoring data to database...")
        store_to_database(market_data, 'market_data.db')
    
    # Also export to CSV for backup
    if market_data:
        print("Exporting data to CSV (backup)...")
        export_to_csv(market_data, config.OUTPUT_FILENAME)
    
    # Print summary
    duration = (end_time - start_time).total_seconds()
    print(f"\n{'='*60}")
    print(f"Execution Summary")
    print(f"{'='*60}")
    print(f"Total time: {duration:.2f} seconds")
    print(f"Markets processed: {len(market_data)}")
    print(f"Categories: {len(config.CATEGORIES)}")
    print(f"Primary database: market_data.db")
    print(f"Backup CSV: {config.OUTPUT_FILENAME}")
    print(f"{'='*60}\n")
    
    print("\nWeb viewer is running. Press Ctrl+C to stop.")
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nStopping...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[ERROR] Process interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
