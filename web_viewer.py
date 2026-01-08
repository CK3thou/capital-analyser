"""
Web-based viewer for Capital.com market analysis results
Auto-fetches fresh data from API on startup
"""

from flask import Flask, render_template, jsonify, request
import csv
import os
from datetime import datetime
import threading
import sys
import time

app = Flask(__name__)

# Global variable to track refresh status
refresh_status = {
    'in_progress': False,
    'last_refresh': None,
    'status_message': 'Ready'
}

def load_market_data():
    """Load market data from CSV file"""
    csv_file = 'capital_markets_analysis.csv'
    
    if not os.path.exists(csv_file):
        return []
    
    markets = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            markets.append(row)
    
    return markets

def get_file_stats():
    """Get statistics about the data file"""
    csv_file = 'capital_markets_analysis.csv'
    
    if not os.path.exists(csv_file):
        return None
    
    stats = {
        'file_size': os.path.getsize(csv_file),
        'modified_time': datetime.fromtimestamp(os.path.getmtime(csv_file)).strftime('%Y-%m-%d %H:%M:%S'),
        'exists': True
    }
    
    return stats

def get_dashboard_stats():
    """Get dashboard statistics"""
    markets = load_market_data()
    
    if not markets:
        return {
            'total_markets': 0,
            'total_categories': 0,
            'best_performer': None,
            'last_fetch': 'N/A'
        }
    
    # Count total markets and categories
    categories = set()
    best_performer = None
    best_value = float('-inf')
    
    for market in markets:
        categories.add(market.get('Category', 'Unknown'))
        
        # Find best performer by 1M performance
        perf_1m = market.get('Perf % 1M', 'N/A')
        if perf_1m != 'N/A':
            try:
                value = float(perf_1m.rstrip('%'))
                if value > best_value:
                    best_value = value
                    best_performer = {
                        'name': market.get('Symbol', 'N/A'),
                        'value': perf_1m
                    }
            except (ValueError, AttributeError):
                pass
    
    file_stats = get_file_stats()
    last_fetch = file_stats['modified_time'] if file_stats else 'N/A'
    
    return {
        'total_markets': len(markets),
        'total_categories': len(categories),
        'best_performer': best_performer,
        'last_fetch': last_fetch
    }

def refresh_market_data_background():
    """Background thread function to fetch fresh data from API"""
    global refresh_status
    
    refresh_status['in_progress'] = True
    refresh_status['status_message'] = 'Connecting to Capital.com API...'
    
    try:
        # Import here to avoid circular dependencies
        from capital_analyzer import CapitalAPI
        import config
        
        print("\n" + "="*60)
        print("AUTO-REFRESH: Fetching fresh data from Capital.com API")
        print("="*60)
        
        refresh_status['status_message'] = 'Initializing API connection...'
        
        # Create API client
        api = CapitalAPI(
            api_key=config.API_KEY,
            identifier=config.USERNAME,
            password=config.PASSWORD,
            demo=config.USE_DEMO
        )
        
        # Create session
        if not api.create_session():
            raise Exception("Failed to create API session")
        
        refresh_status['status_message'] = 'Fetching market data from API...'
        
        # Fetch and analyze markets
        all_data = []
        categories = config.CATEGORIES
        
        for category in categories:
            print(f"Fetching {category}...")
            refresh_status['status_message'] = f'Fetching {category}...'
            
            # Fetch markets in this category
            markets = api.get_markets_by_category(category)
            
            if not markets:
                print(f"  No markets found in {category}")
                continue
            
            # Limit per category
            limit = 20 if category != 'commodities' else None
            if limit:
                markets = markets[:limit]
            
            for idx, market in enumerate(markets, 1):
                try:
                    epic = market.get('epic')
                    name = market.get('instrumentName', epic)
                    
                    # Get market details
                    details = api.get_market_details(epic)
                    if not details:
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
                    
                    # Rate limiting
                    time.sleep(0.15)
                    
                    # Ping session every 20 requests
                    if idx % 20 == 0:
                        api.ping()
                
                except Exception as e:
                    print(f"  Error processing {epic}: {e}")
                    continue
        
        # Export to CSV
        if all_data:
            refresh_status['status_message'] = f'Saving {len(all_data)} markets to CSV...'
            export_to_csv(all_data, 'capital_markets_analysis.csv')
            refresh_status['last_refresh'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            refresh_status['status_message'] = f'✓ Updated {len(all_data)} markets'
            print(f"✓ AUTO-REFRESH: Updated {len(all_data)} markets successfully")
        else:
            refresh_status['status_message'] = 'No data retrieved'
        
    except Exception as e:
        error_msg = f"Error fetching data: {str(e)}"
        refresh_status['status_message'] = error_msg
        print(f"✗ AUTO-REFRESH FAILED: {error_msg}")
    
    finally:
        refresh_status['in_progress'] = False
        print("="*60 + "\n")

def format_percentage(value: float) -> str:
    """Format percentage value for display"""
    if value is None:
        return "N/A"
    return f"{value:.2f}%"

@app.route('/')
def index():
    """Main page"""
    stats = get_dashboard_stats()
    return render_template('index.html', stats=stats)

@app.route('/api/markets')
def get_markets():
    """API endpoint to get market data"""
    markets = load_market_data()
    stats = get_file_stats()
    
    return jsonify({
        'markets': markets,
        'stats': stats,
        'count': len(markets)
    })

@app.route('/api/categories')
def get_categories():
    """Get unique categories"""
    markets = load_market_data()
    categories = list(set(m.get('Category', 'Unknown') for m in markets))
    
    return jsonify({
        'categories': sorted(categories),
        'count': len(categories)
    })

@app.route('/api/top-performers')
def get_top_performers():
    """Get top performers by category and timeframe"""
    markets = load_market_data()
    timeframe = request.args.get('timeframe', 'Perf % 1M')
    
    # Map timeframe parameter to CSV column name
    timeframe_map = {
        'Perf % 1D': 'Perf % 1D',
        'Perf % 1W': 'Perf % 1W',
        'Perf % 1M': 'Perf % 1M',
        'Perf % 3M': 'Perf % 3M',
        'Perf % 6M': 'Perf % 6M',
        'Perf % YTD': 'Perf % YTD',
        'Perf % 1Y': 'Perf % 1Y',
        'Perf % 5Y': 'Perf % 5Y',
        'Perf % 10Y': 'Perf % 10Y',
    }
    
    column = timeframe_map.get(timeframe, 'Perf % 1M')
    
    # Group by category and find top 5 performers
    results = {}
    for market in markets:
        category = market.get('Category', 'Unknown')
        if category not in results:
            results[category] = []
        
        perf_value = market.get(column, 'N/A')
        # Always add markets, even if performance is N/A
        results[category].append({
            'symbol': market.get('Symbol', 'N/A'),
            'name': market.get('Name', 'N/A'),
            'performance': perf_value  # Use the formatted string for display
        })
    
    # Sort each category by performance and get top 5
    def sort_key(item):
        perf = item['performance']
        if perf == 'N/A':
            return float('-inf')
        try:
            return float(perf.rstrip('%'))
        except (ValueError, AttributeError, TypeError):
            return float('-inf')
    
    for category in results:
        results[category] = sorted(
            results[category],
            key=sort_key,
            reverse=True
        )[:5]
    
    return jsonify(results)

@app.route('/api/refresh-status')
def get_refresh_status():
    """Get current refresh status"""
    return jsonify(refresh_status)

@app.route('/api/refresh-now', methods=['POST'])
def refresh_now():
    """Trigger immediate data refresh"""
    if not refresh_status['in_progress']:
        import threading
        thread = threading.Thread(target=refresh_market_data_background, daemon=True)
        thread.start()
        return jsonify({'status': 'refresh started'})
    return jsonify({'status': 'refresh already in progress'}), 429

def export_to_csv(data: list, filename: str):
    """Export market data to CSV file"""
    if not data:
        return
    
    # Define column order
    fieldnames = [
        'Category', 'Symbol', 'Name', 'Current Price', 'Currency',
        'Price Change %', 'Perf % 1D', 'Perf % 1W', 'Perf % 1M', 'Perf % 3M',
        'Perf % 6M', 'Perf % YTD', 'Perf % 1Y', 'Perf % 5Y', 'Perf % 10Y',
        'Market Status', 'Type'
    ]
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
    except Exception as e:
        print(f"Error exporting to CSV: {e}")

if __name__ == '__main__':
    print("="*60)
    print("Capital.com Market Analyzer - Web Viewer")
    print("="*60)
    print("\nStarting web server...")
    print("Open your browser and go to: http://localhost:5000")
    print("\nStarting auto-refresh in background...")
    print("="*60)
    
    # Start background refresh thread
    refresh_thread = threading.Thread(target=refresh_market_data_background, daemon=True)
    refresh_thread.start()
    
    # Start Flask web server
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
