# Capital.com Market Analyzer - Project Summary

## What Has Been Created

A complete Python application to fetch, categorize, and analyze market symbols from Capital.com with performance metrics.

## Files Created

### Core Application Files

1. **`capital_analyzer.py`** (Main API Client)
   - `CapitalAPI` class for session management
   - Methods to fetch markets by category (commodities, forex, indices, crypto, shares)
   - Historical price fetching
   - Performance calculation engine
   - Automatic session renewal and rate limiting

2. **`run_analyzer.py`** (Main Execution Script)
   - Orchestrates the entire analysis workflow
   - Fetches all markets across selected categories
   - Calculates performance metrics
   - Exports to CSV with proper formatting
   - Progress tracking and error handling

3. **`view_results.py`** (Results Viewer)
   - Terminal-based CSV viewer
   - Shows summary statistics by category
   - Displays top/bottom performers
   - Quick analysis without opening Excel

### Configuration Files

4. **`config_template.py`** (Configuration Template)
   - Template for user credentials
   - Customizable settings (categories, limits, output filename)
   - Environment selection (Demo/Live)

5. **`requirements.txt`** (Dependencies)
   - Python package requirements
   - Minimal dependencies (requests, python-dateutil)

### Documentation Files

7. **`README_ANALYZER.md`** (Full Documentation)
   - Complete feature overview
   - Detailed installation instructions
   - Configuration guide
   - Troubleshooting section
   - API limits and best practices

8. **`QUICKSTART.md`** (Quick Start Guide)
   - 5-minute setup guide
   - Step-by-step instructions
   - Common issues and solutions
   - Tips for faster results

## Features Implemented

### ✅ Market Categorization
- **Commodities**: Gold, Silver, Oil, Natural Gas, etc.
- **Forex**: EUR/USD, GBP/USD, USD/JPY, etc.
- **Indices**: S&P 500, NASDAQ, FTSE 100, etc.
- **Cryptocurrencies**: Bitcoin, Ethereum, etc.
- **Shares**: Stocks and ETFs

### ✅ Performance Metrics (All Requested)
- **Price Change %**: Current day percentage change
- **Perf % 1W**: 1 week performance
- **Perf % 1M**: 1 month performance
- **Perf % 3M**: 3 months performance
- **Perf % 6M**: 6 months performance
- **Perf % YTD**: Year-to-date performance
- **Perf % 1Y**: 1 year performance
- **Perf % 5Y**: 5 years performance
- **Perf % 10Y**: 10 years performance
- **Perf % All Time**: Maximum historical performance (where data exists)

### ✅ CSV Export with Columns
The output CSV includes:
```
Category | Symbol | Name | Current Price | Currency | 
Price Change % | Perf % 1W | Perf % 1M | Perf % 3M | 
Perf % 6M | Perf % YTD | Perf % 1Y | Perf % 5Y | 
Perf % 10Y | Market Status | Type
```

### ✅ Additional Features
- Automatic session management
- Rate limiting (respects 10 req/sec API limit)
- Session keep-alive (auto ping every 20 requests)
- Configurable market limits
- Progress tracking
- Error handling
- Terminal-based results viewer

## How to Use

### Initial Setup
```powershell
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure credentials
Copy-Item config_template.py config.py
notepad config.py  # Add your API key, username, password

# 3. Run the analyzer
python run_analyzer.py

# 4. View results
python view_results.py
# Or open capital_markets_analysis.csv in Excel
```

### Customization
Edit `config.py` to:
- Select specific categories to analyze
- Limit number of markets per category
- Change output filename
- Adjust rate limiting delay
- Switch between Demo and Live environments

## Technical Details

### API Integration
- Uses Capital.com REST API v1
- Session-based authentication with CST and X-SECURITY-TOKEN
- Endpoints used:
  - `POST /session` - Authentication
  - `GET /ping` - Keep-alive
  - `GET /marketnavigation/{nodeId}` - Fetch markets by category
  - `GET /markets/{epic}` - Market details
  - `GET /prices/{epic}` - Historical prices

### Performance Calculation Logic
1. Fetches current market snapshot for latest price
2. Calculates historical dates (e.g., 7 days ago, 30 days ago, etc.)
3. Retrieves historical prices for each period
4. Computes percentage change: `((current - old) / old) * 100`
5. Handles missing data gracefully (shows "N/A")

### Rate Limiting
- Default 0.15 second delay between requests (6-7 req/sec)
- Session ping every 20 requests
- Respects API limit of 10 req/sec

## Example Output

### CSV Format
```csv
Category,Symbol,Name,Current Price,Currency,Price Change %,Perf % 1W,...
Commodities,GOLD,Gold,1895.50,USD,0.45%,2.30%,5.67%,...
Forex,EURUSD,EUR/USD,1.0832,USD,-0.12%,-0.45%,1.23%,...
Cryptocurrencies,BITCOIN,Bitcoin,43250.00,USD,3.45%,8.90%,15.67%,...
```

### Terminal Viewer Output
```
===================================================================
SUMMARY
===================================================================
Total Markets: 245

Breakdown by Category:
  Commodities         :   45 markets
  Cryptocurrencies    :   35 markets
  Forex              :   85 markets
  Indices            :   50 markets
  Shares             :   30 markets
===================================================================

TOP 5 PERFORMERS - Perf % 1M
===================================================================
Rank   Symbol          Name                           Perf % 1M
--------------------------------------------------------------------------------
1      BITCOIN         Bitcoin                           15.67%
2      ETHEREUM        Ethereum                          12.34%
...
```

## Known Limitations

1. **Historical Data Availability**: 
   - Not all markets have 5Y or 10Y historical data
   - Newer markets will show "N/A" for long-term metrics

2. **API Rate Limits**:
   - Maximum 10 requests per second
   - Session expires after 10 minutes of inactivity

3. **Execution Time**:
   - Fetching all markets can take 10-30 minutes
   - Each market requires 2-10 API calls (details + historical prices)
   - Use `MAX_MARKETS_PER_CATEGORY` to limit for faster testing

4. **All Time Performance**:
   - Limited by available historical data
   - Capital.com API doesn't provide inception dates

## Future Enhancement Ideas

- [ ] Export to Excel with formatting and charts
- [ ] Real-time WebSocket price updates
- [ ] Database storage for historical tracking
- [ ] Web dashboard with interactive charts
- [ ] Email/Slack alerts for top performers
- [ ] Comparison with benchmark indices
- [ ] Volatility metrics (ATR, standard deviation)
- [ ] Dividend yield for shares
- [ ] Multi-timeframe analysis

## Security Considerations

- ✅ Template file (`config_template.py`) with placeholders
- ✅ Credentials never hardcoded
- ⚠️  Use Demo account for testing
- ⚠️  Store API key securely
- ⚠️  Never share `config.py` file

## Support Resources

- **Capital.com API Docs**: https://capital.com/api
- **API Specification**: https://open-api.capital.com/
- **API FAQ**: https://capital.zendesk.com/hc/en-us/sections/4415178206354-API
- **Support Email**: support@capital.com

## License

Follows the same license as the original Capital.com Postman collection (MIT).
