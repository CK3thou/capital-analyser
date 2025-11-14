"""
Main script to fetch and analyze Capital.com markets
"""

import csv
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
    print("✗ config.py not found!")
    print("Please copy config_template.py to config.py and fill in your credentials.")
    sys.exit(1)


def format_percentage(value: float) -> str:
    """Format percentage value for display"""
    if value is None:
        return "N/A"
    return f"{value:.2f}%"


def fetch_and_analyze_markets(api: CapitalAPI, categories: list) -> list:
    """
    Fetch all markets and calculate performance metrics
    
    Returns:
        List of dictionaries with market data and performance metrics
    """
    # Category-specific limits
    CATEGORY_LIMITS = {
        'forex': 20,
        'commodities': None,  # No limit - list all
        'shares': 50,
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
    print(f"✓ Completed! Processed {total_markets} markets across {len(categories)} categories")
    print(f"{'='*60}\n")
    
    return all_data


def export_to_csv(data: list, filename: str):
    """Export market data to CSV file"""
    if not data:
        print("✗ No data to export")
        return
    
    # Define column order
    fieldnames = [
        'Category',
        'Symbol',
        'Name',
        'Current Price',
        'Currency',
        'Price Change %',
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
        
        print(f"✓ Data exported to: {filename}")
        print(f"  Total rows: {len(data)}")
    except Exception as e:
        print(f"✗ Error exporting to CSV: {str(e)}")


def main():
    """Main execution function"""
    print("="*60)
    print("Capital.com Market Analyzer")
    print("="*60)
    print(f"Environment: {'DEMO' if config.USE_DEMO else 'LIVE'}")
    print(f"Categories: {', '.join(config.CATEGORIES)}")
    print(f"Output file: {config.OUTPUT_FILENAME}")
    print("="*60)
    
    # Initialize API client
    print("\nInitializing API client...")
    api = CapitalAPI(
        api_key=config.API_KEY,
        identifier=config.USERNAME,
        password=config.PASSWORD,
        demo=config.USE_DEMO
    )
    
    # Create session
    if not api.create_session():
        print("✗ Failed to create session. Please check your credentials.")
        return
    
    # Fetch and analyze markets
    start_time = datetime.now()
    market_data = fetch_and_analyze_markets(api, config.CATEGORIES)
    end_time = datetime.now()
    
    # Export to CSV
    if market_data:
        export_to_csv(market_data, config.OUTPUT_FILENAME)
    
    # Print summary
    duration = (end_time - start_time).total_seconds()
    print(f"\n{'='*60}")
    print(f"Execution Summary")
    print(f"{'='*60}")
    print(f"Total time: {duration:.2f} seconds")
    print(f"Markets processed: {len(market_data)}")
    print(f"Categories: {len(config.CATEGORIES)}")
    print(f"{'='*60}\n")
    
    # Launch web viewer
    print("Launching web viewer...")
    print("Opening browser at http://localhost:5000")
    import webbrowser
    import threading
    import subprocess
    
    # Start web server in background
    def start_web_server():
        subprocess.run([sys.executable, "web_viewer.py"], cwd=os.path.dirname(os.path.abspath(__file__)))
    
    server_thread = threading.Thread(target=start_web_server, daemon=True)
    server_thread.start()
    
    # Wait a moment for server to start
    time.sleep(2)
    
    # Open browser
    webbrowser.open('http://localhost:5000')
    
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
        print("\n\n✗ Process interrupted by user")
    except Exception as e:
        print(f"\n✗ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
