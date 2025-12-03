"""
Flask web app for Capital.com Market Analyzer
Clean, lightweight alternative to Streamlit with SQLite database
"""

from flask import Flask, render_template, request, jsonify
import pandas as pd
import sqlite3
import os
from datetime import datetime
from pathlib import Path

app = Flask(__name__)

# Configuration
DB_PATH = 'market_data.db'
CSV_FILE = 'capital_markets_analysis.csv'


def init_db():
    """Initialize SQLite database"""
    conn = sqlite3.connect(DB_PATH)
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
            perf_30m_pct REAL,
            perf_1h_pct REAL,
            perf_4h_pct REAL,
            perf_6h_pct REAL,
            perf_1d_pct REAL,
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


def import_csv_to_db(csv_file):
    """Import CSV data into SQLite"""
    if not os.path.exists(csv_file):
        return False
    
    try:
        df = pd.read_csv(csv_file)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Clear existing data
        cursor.execute('DELETE FROM markets')
        
        for _, row in df.iterrows():
            def parse_pct(val):
                if pd.isna(val) or val == 'N/A':
                    return None
                if isinstance(val, str):
                    try:
                        return float(val.replace('%', '').strip())
                    except (ValueError, AttributeError):
                        return None
                return float(val)
            
            cursor.execute('''
                INSERT INTO markets (
                    category, symbol, name, current_price, currency,
                    price_change_pct, perf_30m_pct, perf_1h_pct, perf_4h_pct,
                    perf_6h_pct, perf_1d_pct, perf_1w_pct, perf_1m_pct, perf_3m_pct,
                    perf_6m_pct, perf_ytd_pct, perf_1y_pct, perf_5y_pct,
                    perf_10y_pct, market_status, type
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                row.get('Category', ''),
                row.get('Symbol', ''),
                row.get('Name', ''),
                parse_pct(row.get('Current Price', None)),
                row.get('Currency', ''),
                parse_pct(row.get('Price Change %', None)),
                parse_pct(row.get('Perf % 30M', None)),
                parse_pct(row.get('Perf % 1H', None)),
                parse_pct(row.get('Perf % 4H', None)),
                parse_pct(row.get('Perf % 6H', None)),
                parse_pct(row.get('Perf % 1D', None)),
                parse_pct(row.get('Perf % 1W', None)),
                parse_pct(row.get('Perf % 1M', None)),
                parse_pct(row.get('Perf % 3M', None)),
                parse_pct(row.get('Perf % 6M', None)),
                parse_pct(row.get('Perf % YTD', None)),
                parse_pct(row.get('Perf % 1Y', None)),
                parse_pct(row.get('Perf % 5Y', None)),
                parse_pct(row.get('Perf % 10Y', None)),
                row.get('Market Status', ''),
                row.get('Type', '')
            ))
        
        # Update metadata
        cursor.execute('DELETE FROM metadata WHERE key = ?', ('last_fetch_time',))
        cursor.execute(
            'INSERT INTO metadata (key, value) VALUES (?, ?)',
            ('last_fetch_time', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        )
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error importing CSV: {e}")
        return False


def get_last_fetch_time():
    """Get last data fetch timestamp"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT value FROM metadata WHERE key = ?', ('last_fetch_time',))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else "Never"
    except:
        return "Unknown"


def load_markets_from_db(category=None, search=None):
    """Load markets from SQLite"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = 'SELECT * FROM markets WHERE 1=1'
        params = []
        
        if category and category != 'All':
            query += ' AND category = ?'
            params.append(category)
        
        if search:
            query += ' AND (name LIKE ? OR symbol LIKE ?)'
            params.extend([f'%{search}%', f'%{search}%'])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Error loading markets: {e}")
        return []


def get_categories():
    """Get all categories"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT category FROM markets ORDER BY category')
        categories = [row[0] for row in cursor.fetchall()]
        conn.close()
        return ['All'] + categories
    except:
        return ['All']


def get_top_performers(timeframe):
    """Get top performers by category for a timeframe"""
    perf_col_map = {
        '30M': 'perf_30m_pct',
        '1H': 'perf_1h_pct',
        '4H': 'perf_4h_pct',
        '6H': 'perf_6h_pct',
        '1D': 'perf_1d_pct',
        '1W': 'perf_1w_pct',
        '1M': 'perf_1m_pct',
        '3M': 'perf_3m_pct',
        '6M': 'perf_6m_pct',
        'YTD': 'perf_ytd_pct',
        '1Y': 'perf_1y_pct',
        '5Y': 'perf_5y_pct',
        '10Y': 'perf_10y_pct'
    }
    
    col_name = perf_col_map.get(timeframe, 'perf_1m_pct')
    
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT DISTINCT category FROM markets ORDER BY category')
        categories = [row[0] for row in cursor.fetchall()]
        
        top_performers = {}
        for category in categories:
            cursor.execute(f'''
                SELECT name, symbol, {col_name} as perf
                FROM markets
                WHERE category = ? AND {col_name} IS NOT NULL
                ORDER BY {col_name} DESC
                LIMIT 5
            ''', (category,))
            
            performers = []
            for row in cursor.fetchall():
                performers.append({
                    'name': row['name'],
                    'symbol': row['symbol'],
                    'performance': f"{row['perf']:.2f}%" if row['perf'] is not None else 'N/A'
                })
            
            top_performers[category] = performers
        
        conn.close()
        return top_performers
    except Exception as e:
        print(f"Error getting top performers: {e}")
        return {}


@app.route('/')
def index():
    """Main dashboard"""
    markets = load_markets_from_db()
    
    if not markets:
        return render_template('index.html', 
                             error='No data available. Please run run_analyzer.py first.',
                             stats={})
    
    # Calculate statistics
    stats = {
        'total_markets': len(markets),
        'total_categories': len(set(m['category'] for m in markets)),
        'last_fetch': get_last_fetch_time()
    }
    
    # Best performer (1M)
    best = max([m for m in markets if m['perf_1m_pct'] is not None], 
               key=lambda x: x['perf_1m_pct'], default=None)
    if best:
        stats['best_performer'] = {
            'name': best['name'],
            'symbol': best['symbol'],
            'value': f"{best['perf_1m_pct']:.2f}%"
        }
    
    return render_template('index.html', stats=stats)


@app.route('/api/markets')
def api_markets():
    """API endpoint for market data"""
    category = request.args.get('category', 'All')
    search = request.args.get('search', '').lower()
    
    markets = load_markets_from_db(category if category != 'All' else None, search)
    
    return jsonify([{
        'id': m['id'],
        'Category': m['category'],
        'Symbol': m['symbol'],
        'Name': m['name'],
        'Current Price': m['current_price'],
        'Currency': m['currency'],
        'perf_30m': m['perf_30m_pct'],
        'perf_1h': m['perf_1h_pct'],
        'perf_4h': m['perf_4h_pct'],
        'perf_6h': m['perf_6h_pct'],
        'perf_1d': m['perf_1d_pct'],
        'perf_1w': m['perf_1w_pct'],
        'perf_1m': m['perf_1m_pct'],
        'perf_3m': m['perf_3m_pct'],
        'perf_6m': m['perf_6m_pct'],
        'perf_ytd': m['perf_ytd_pct'],
        'perf_1y': m['perf_1y_pct'],
        'perf_5y': m['perf_5y_pct'],
        'perf_10y': m['perf_10y_pct']
    } for m in markets])


@app.route('/api/categories')
def api_categories():
    """Get list of categories"""
    return jsonify(get_categories())


@app.route('/api/top-performers')
def api_top_performers():
    """Get top performers by category"""
    timeframe = request.args.get('timeframe', '1M')
    return jsonify(get_top_performers(timeframe))


@app.route('/api/stats')
def api_stats():
    """Get statistics"""
    return jsonify({
        'last_fetch': get_last_fetch_time()
    })


if __name__ == '__main__':
    # Initialize database
    init_db()
    
    # Import CSV data if available
    if os.path.exists(CSV_FILE):
        import_csv_to_db(CSV_FILE)
        print(f"✓ Data imported from {CSV_FILE}")
    
    print("Starting Capital.com Market Analyzer Web App")
    print("Access at: http://localhost:5000")
    app.run(debug=False, host='localhost', port=5000)
