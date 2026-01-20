"""
Web-based viewer for Capital.com market analysis results
"""

from flask import Flask, render_template, jsonify
import os
from datetime import datetime
import database  # Import database module

app = Flask(__name__)

def load_market_data():
    """Load market data from SQLite database"""
    return database.load_market_data_list()

def get_file_stats():
    """Get statistics about the database"""
    return database.get_db_stats()

@app.route('/')
def index():
    """Main page"""
    stats = get_file_stats()
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

if __name__ == '__main__':
    print("="*60)
    print("Capital.com Market Analyzer - Web Viewer")
    print("="*60)
    print("\nStarting web server...")
    print("Open your browser and go to: http://localhost:5000")
    print("\nPress Ctrl+C to stop the server")
    print("="*60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
