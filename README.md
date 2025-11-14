# Capital.com Market Analyzer

A Python application that fetches and analyzes market data from Capital.com API, displaying results in a beautiful, responsive web interface.

## Features

- 📊 **Market Data Fetching**: Automatically retrieves market data across multiple categories (Commodities, Forex, Indices, Cryptocurrencies, Shares)
- 📈 **Performance Metrics**: Calculates performance for multiple time periods (1W, 1M, 3M, 6M, YTD, 1Y, 5Y, 10Y)
- 🌐 **Web Interface**: Beautiful, responsive dark-themed web UI
- 🔍 **Search & Filter**: Real-time search and category filtering
- 📱 **Mobile Responsive**: Works perfectly on all devices
- 🚀 **Auto-Launch**: Automatically opens web browser when run

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure your credentials:
```bash
cp config_template.py config.py
```

Edit `config.py` and add your Capital.com API credentials:
- API Key
- Username (email)
- Password

## Web Interface

The web interface includes:
- Statistics dashboard
- Real-time search
- Category filtering
- Sortable columns
- Color-coded performance metrics
- Auto-refresh functionality

Access at: http://localhost:5000

## Project Structure

- `capital_analyzer.py` - Core API client
- `run_analyzer.py` - Main execution script
- `web_viewer.py` - Flask web server
- `templates/index.html` - Web interface
- `config.py` - Configuration (not in repo)
- `requirements.txt` - Python dependencies

## Technologies

- Python 3.x
- Flask (Web framework)
- Capital.com REST API
- HTML/CSS/JavaScript

## License

MIT License
