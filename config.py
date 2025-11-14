"""
Configuration file for Capital.com Market Analyzer
Copy this to config.py and fill in your credentials
"""

# Capital.com API Configuration
# Get your API key from: Settings > API integrations > Generate new key

API_KEY = "MDQRi4km1ODEzGeF"
USERNAME = "chishimba.kabwe@gmail.com"
PASSWORD = "-Cullbanga#1"

# Environment Selection
# Set to True for demo/sandbox environment
# Set to False for live trading environment
USE_DEMO = True

# Export Settings
OUTPUT_FILENAME = "capital_markets_analysis.csv"

# Categories to fetch (comment out any you don't want)
CATEGORIES = [
    'commodities',
    'forex',
    'indices',
    'cryptocurrencies',
    'shares',  # Includes ETFs
]

# Rate limiting (seconds to wait between API calls)
REQUEST_DELAY = 0.15

# Maximum markets to fetch per category (set to None for all)
MAX_MARKETS_PER_CATEGORY = None  # Fetch all markets
