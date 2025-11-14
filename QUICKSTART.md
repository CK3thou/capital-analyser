# Quick Start Guide - Capital.com Market Analyzer

## 5-Minute Setup

### Step 1: Get Your API Credentials

1. Go to https://capital.com (or demo site)
2. Enable 2FA: Settings → Security → Two-Factor Authentication
3. Generate API Key: Settings → API integrations → Generate new key
4. **Save your API key** (shown only once!)

### Step 2: Install Dependencies

```powershell
pip install -r requirements.txt
```

### Step 3: Configure Credentials

```powershell
# Copy template
Copy-Item config_template.py config.py

# Edit with your credentials
notepad config.py
```

Update these lines in `config.py`:
```python
API_KEY = "your-api-key-from-step-1"
USERNAME = "your-email@example.com"
PASSWORD = "your-password"
USE_DEMO = True  # Keep True for testing
```

### Step 4: Run the Analyzer

```powershell
python run_analyzer.py
```

### Step 5: View Results

Open `capital_markets_analysis.csv` in Excel or any spreadsheet software.

---

## What You'll Get

A CSV file with columns:
- **Category**: Commodities, Forex, Indices, Cryptocurrencies, Shares
- **Symbol & Name**: Market identifier and full name
- **Current Price**: Latest bid price
- **Price Change %**: Today's change
- **Perf % 1W, 1M, 3M, 6M**: Short to medium term performance
- **Perf % YTD, 1Y, 5Y, 10Y**: Long term performance

---

## Common Issues

**"Session creation failed"**
→ Double-check API_KEY, USERNAME, PASSWORD in config.py

**"config.py not found"**
→ Copy config_template.py to config.py first

**"Import requests not found"**
→ Run: `pip install -r requirements.txt`

---

## Tips for Faster Results

Edit `config.py` to limit markets:

```python
# Only fetch first 20 markets per category
MAX_MARKETS_PER_CATEGORY = 20

# Or analyze only specific categories
CATEGORIES = [
    'cryptocurrencies',  # Just crypto
]
```

---

## Need Help?

- Capital.com API Docs: https://capital.com/api
- Full Documentation: See README_ANALYZER.md
- API Support: support@capital.com
