"""
Web-based viewer for Capital.com market analysis results
"""

from flask import Flask, render_template, jsonify
import csv
import os
from datetime import datetime

app = Flask(__name__)

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

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

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

if __name__ == '__main__':
    print("="*60)
    print("Capital.com Market Analyzer - Web Viewer")
    print("="*60)
    print("\nStarting web server...")
    print("Open your browser and go to: http://localhost:5000")
    print("\nPress Ctrl+C to stop the server")
    print("="*60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
