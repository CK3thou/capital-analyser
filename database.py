"""
Database module for Capital.com Market Analyzer
Handles SQLite database operations
"""

import sqlite3
import pandas as pd
import os
from datetime import datetime

DB_FILE = 'market_data.db'

def get_db_connection():
    """Create a database connection"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with required tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create markets table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS markets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT,
        symbol TEXT UNIQUE,
        name TEXT,
        current_price REAL,
        currency TEXT,
        price_change_pct TEXT,
        perf_1w TEXT,
        perf_1m TEXT,
        perf_3m TEXT,
        perf_6m TEXT,
        perf_ytd TEXT,
        perf_1y TEXT,
        perf_5y TEXT,
        perf_10y TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create metadata table for storing fetch timestamps and other metadata
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS metadata (
        key TEXT PRIMARY KEY,
        value TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()

def save_market_data(data):
    """
    Save market data to the database
    
    Args:
        data (list): List of dictionaries containing market data
    """
    if not data:
        return
        
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Clear existing data to ensure fresh snapshot (optional, depending on requirement)
    # For now, we'll replace existing records or insert new ones
    
    # Prepare data for insertion
    # We use INSERT OR REPLACE to handle updates
    for item in data:
        cursor.execute('''
        INSERT OR REPLACE INTO markets (
            category, symbol, name, current_price, currency, 
            price_change_pct, perf_1w, perf_1m, perf_3m, 
            perf_6m, perf_ytd, perf_1y, perf_5y, perf_10y,
            updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            item.get('Category'),
            item.get('Symbol'),
            item.get('Name'),
            item.get('Current Price'),
            item.get('Currency'),
            item.get('Price Change %'),
            item.get('Perf % 1W'),
            item.get('Perf % 1M'),
            item.get('Perf % 3M'),
            item.get('Perf % 6M'),
            item.get('Perf % YTD'),
            item.get('Perf % 1Y'),
            item.get('Perf % 5Y'),
            item.get('Perf % 10Y'),
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ))
    
    conn.commit()
    conn.close()

def load_market_data_df():
    """Load market data into a pandas DataFrame"""
    if not os.path.exists(DB_FILE):
        return None
        
    conn = get_db_connection()
    try:
        df = pd.read_sql_query("SELECT * FROM markets", conn)
        
        # Rename columns to match the expected format in the app
        # The DB columns are snake_case, app expects Title Case with spaces
        column_mapping = {
            'category': 'Category',
            'symbol': 'Symbol',
            'name': 'Name',
            'current_price': 'Current Price',
            'currency': 'Currency',
            'price_change_pct': 'Price Change %',
            'perf_1w_pct': 'Perf % 1W',
            'perf_1m_pct': 'Perf % 1M',
            'perf_3m_pct': 'Perf % 3M',
            'perf_6m_pct': 'Perf % 6M',
            'perf_ytd_pct': 'Perf % YTD',
            'perf_1y_pct': 'Perf % 1Y',
            'perf_5y_pct': 'Perf % 5Y',
            'perf_10y_pct': 'Perf % 10Y',
            'market_status': 'Market Status',
            'type': 'Type'
        }
        df = df.rename(columns=column_mapping)
        return df
    except Exception as e:
        print(f"Error loading data from DB: {e}")
        return None
    finally:
        conn.close()

def load_market_data_list():
    """Load market data as a list of dictionaries"""
    if not os.path.exists(DB_FILE):
        return []
        
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT * FROM markets")
        rows = cursor.fetchall()
        
        result = []
        for row in rows:
            item = dict(row)
            # Map keys to match expected format
            mapped_item = {
                'Category': item['category'],
                'Symbol': item['symbol'],
                'Name': item['name'],
                'Current Price': item['current_price'],
                'Currency': item['currency'],
                'Price Change %': item['price_change_pct'],
                'Perf % 1W': item['perf_1w_pct'],
                'Perf % 1M': item['perf_1m_pct'],
                'Perf % 3M': item['perf_3m_pct'],
                'Perf % 6M': item['perf_6m_pct'],
                'Perf % YTD': item['perf_ytd_pct'],
                'Perf % 1Y': item['perf_1y_pct'],
                'Perf % 5Y': item['perf_5y_pct'],
                'Perf % 10Y': item['perf_10y_pct']
            }
            result.append(mapped_item)
            
        return result
    except Exception as e:
        print(f"Error loading data from DB: {e}")
        return []
    finally:
        conn.close()

def get_last_updated():
    """Get the timestamp of the last update formatted nicely"""
    if not os.path.exists(DB_FILE):
        return None
        
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Query the metadata table for the last_fetch_time (set by run_analyzer.py)
        cursor.execute("SELECT value FROM metadata WHERE key = 'last_fetch_time'")
        result = cursor.fetchone()
        if result and result[0]:
            # Return the raw timestamp (already in 'YYYY-MM-DD HH:MM:SS' format from run_analyzer.py)
            return result[0]
        return None
    except Exception:
        return None
    finally:
        conn.close()

def get_db_stats():
    """Get statistics about the database"""
    if not os.path.exists(DB_FILE):
        return None
        
    stats = {
        'file_size': os.path.getsize(DB_FILE),
        'modified_time': get_last_updated(),
        'exists': True
    }
    return stats
