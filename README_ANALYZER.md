# Capital.com Market Analyzer

A Python application that fetches market symbols from Capital.com API and categorizes them by asset type (Commodities, Forex, ETFs, Indices, Cryptocurrency) with comprehensive performance metrics.

## Features

- **Automatic Categorization**: Markets are automatically grouped into:
  - Commodities (Gold, Silver, Oil, etc.)
  - Forex (Currency pairs)
  - Indices (S&P 500, NASDAQ, etc.)
  - Cryptocurrencies (Bitcoin, Ethereum, etc.)
  - Shares (Stocks and ETFs)

- **Performance Metrics**: Calculates performance percentages for:
  - Price Change % (current day)
  - 1 Week, 1 Month, 3 Months, 6 Months
  - Year-to-Date (YTD)
  - 1 Year, 5 Years, 10 Years
  - All Time (if data available)

- **CSV Export**: Exports all data to a well-formatted CSV file for analysis in Excel or other tools

- **Rate Limiting**: Built-in rate limiting to comply with Capital.com API restrictions (10 requests/second)

## Prerequisites

1. **Capital.com Account**: You need an account (Demo or Live)
   - Sign up at: https://capital.com/trading/signup

2. **Two-Factor Authentication (2FA)**: Must be enabled
   - Instructions: https://capital.zendesk.com/hc/en-us/articles/4403995863314-How-can-I-enable-2FA-

3. **API Key**: Generate from Settings > API integrations
   - Go to Settings → API integrations → Generate new key
   - Save the API key securely (shown only once!)

## Installation

1. **Clone or download this repository**

2. **Install Python dependencies**:
```powershell
pip install -r requirements.txt
```

3. **Configure your credentials**:
```powershell
# Copy the template
Copy-Item config_template.py config.py

# Edit config.py with your credentials
notepad config.py
```

Fill in your credentials in `config.py`:
```python
API_KEY = "your-api-key-here"
USERNAME = "your-email-or-username"
PASSWORD = "your-password"
USE_DEMO = True  # Set to False for live account
```

## Usage

Run the analyzer:
```powershell
python run_analyzer.py
```

The script will:
1. Connect to Capital.com API
2. Fetch all markets across selected categories
3. Calculate performance metrics for each market
4. Export results to `capital_markets_analysis.csv`

### Configuration Options

Edit `config.py` to customize:

```python
# Select which categories to analyze
CATEGORIES = [
    'commodities',
    'forex',
    'indices',
    'cryptocurrencies',
    'shares',  # Includes ETFs
]

# Output filename
OUTPUT_FILENAME = "capital_markets_analysis.csv"

# Limit markets per category (None for all)
MAX_MARKETS_PER_CATEGORY = 50  # Set to None for unlimited

# Rate limiting delay (seconds)
REQUEST_DELAY = 0.15
```

## Output Format

The CSV file includes these columns:

| Column | Description |
|--------|-------------|
| Category | Asset category (Commodities, Forex, etc.) |
| Symbol | Market epic/symbol code |
| Name | Full market name |
| Current Price | Latest bid price |
| Currency | Trading currency |
| Price Change % | Today's percentage change |
| Perf % 1W | 1 week performance |
| Perf % 1M | 1 month performance |
| Perf % 3M | 3 months performance |
| Perf % 6M | 6 months performance |
| Perf % YTD | Year-to-date performance |
| Perf % 1Y | 1 year performance |
| Perf % 5Y | 5 years performance |
| Perf % 10Y | 10 years performance |
| Market Status | TRADEABLE, CLOSED, etc. |
| Type | Instrument type |

## API Rate Limits

Capital.com API has these limits:
- **10 requests per second** per user
- **Session timeout**: 10 minutes (auto-renewed)
- **POST /session limit**: 1 request per second

The application automatically handles:
- Session management and renewal
- Rate limiting between requests
- Session keep-alive pings

## Troubleshooting

### "Session creation failed"
- Verify your API key, username, and password in `config.py`
- Ensure 2FA is enabled on your account
- Check if you're using the correct environment (Demo vs Live)

### "Import config could not be resolved"
- Make sure you've copied `config_template.py` to `config.py`
- The file must be named exactly `config.py`

### Missing performance data
- Some markets may not have historical data for all time periods
- Newer markets won't have 5Y or 10Y data
- This is normal and will show as "N/A" in the CSV

### Slow execution
- Fetching all markets can take time (hundreds of API calls)
- Consider limiting markets per category in `config.py`
- Use `MAX_MARKETS_PER_CATEGORY = 50` for faster testing

## File Structure

```
capital-api-postman-main/
├── capital_analyzer.py      # Main API client class
├── run_analyzer.py          # Main execution script
├── config_template.py       # Configuration template
├── config.py               # Your credentials (create from template)
├── requirements.txt        # Python dependencies
├── README.md              # This file
└── capital_markets_analysis.csv  # Output file (generated)
```

## Security Notes

- **Never commit `config.py`** to version control (contains credentials)
- Keep your API key secure
- Use demo account for testing
- Review Capital.com's API documentation: https://capital.com/api

## API Documentation

- Capital.com API Docs: https://capital.com/api
- API Specification: https://open-api.capital.com/
- API FAQ: https://capital.zendesk.com/hc/en-us/sections/4415178206354-API

## License

See [LICENSE.md](LICENSE.md) for license information.

## Support

For Capital.com API issues:
- Email: support@capital.com
- API FAQ: https://capital.zendesk.com/hc/en-us/sections/4415178206354-API

## Disclaimer

This tool is for informational purposes only. Trading involves risk. Always do your own research and consider consulting with a financial advisor.
