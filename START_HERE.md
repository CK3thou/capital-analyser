# 🚀 Capital.com Market Analyzer

## Complete Application Ready!

I've created a **complete Python application** that fetches market symbols from Capital.com API and categorizes them with comprehensive performance metrics.

---

## 📁 Files Created

### ✅ Application Files (3)
1. **`capital_analyzer.py`** - Core API client (330 lines)
2. **`run_analyzer.py`** - Main execution script (170 lines)
3. **`view_results.py`** - Results viewer (140 lines)

### ⚙️ Configuration (1)
4. **`config_template.py`** - Configuration template

### 📚 Documentation (3)
6. **`README_ANALYZER.md`** - Full documentation
7. **`QUICKSTART.md`** - 5-minute setup guide
8. **`PROJECT_SUMMARY.md`** - Complete project overview

### 🛠️ Utilities (2)
9. **`requirements.txt`** - Python dependencies
10. **`verify_setup.py`** - Setup verification script

---

## 🎯 Features Implemented

### ✅ All Requested Columns
- **Category**: Commodities, Forex, Indices, Cryptocurrencies, Shares/ETFs
- **Symbol** and **Name**
- **Current Price** and **Currency**
- **Price Change %** (today)
- **Perf % 1W** (1 week)
- **Perf % 1M** (1 month)
- **Perf % 3M** (3 months)
- **Perf % 6M** (6 months)
- **Perf % YTD** (year-to-date)
- **Perf % 1Y** (1 year)
- **Perf % 5Y** (5 years)
- **Perf % 10Y** (10 years)
- **Perf % All Time** (maximum historical)

### ✅ Bonus Features
- Automatic categorization by asset type
- CSV export for Excel analysis
- Terminal viewer for quick analysis
- Rate limiting (respects API limits)
- Session management (auto-renewal)
- Progress tracking
- Error handling
- Configurable limits and categories

---

## 🚦 Quick Start (3 Steps)

### Step 1: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 2: Configure
```powershell
Copy-Item config_template.py config.py
notepad config.py
```
Fill in your:
- `API_KEY` (from Capital.com Settings > API integrations)
- `USERNAME` (your email)
- `PASSWORD`

### Step 3: Run
```powershell
# Verify setup (optional)
python verify_setup.py

# Run analyzer
python run_analyzer.py

# View results
python view_results.py
# Or open capital_markets_analysis.csv in Excel
```

---

## 📊 Output Example

### CSV Format
```csv
Category,Symbol,Name,Current Price,Currency,Price Change %,Perf % 1W,Perf % 1M,...
Commodities,GOLD,Gold,1895.50,USD,0.45%,2.30%,5.67%,...
Forex,EURUSD,EUR/USD,1.0832,USD,-0.12%,-0.45%,1.23%,...
Cryptocurrencies,BITCOIN,Bitcoin,43250.00,USD,3.45%,8.90%,15.67%,...
Indices,US500,US 500,4580.25,USD,0.78%,1.20%,3.45%,...
Shares,AAPL,Apple Inc,182.50,USD,1.25%,3.40%,8.90%,...
```

---

## ⚙️ Customization

Edit `config.py` to:

```python
# Analyze only specific categories
CATEGORIES = [
    'cryptocurrencies',  # Only crypto
]

# Limit markets for faster testing
MAX_MARKETS_PER_CATEGORY = 20  # or None for all

# Change output filename
OUTPUT_FILENAME = "my_analysis.csv"
```

---

## 📖 Documentation Guide

- **First time?** → Read `QUICKSTART.md`
- **Need details?** → Read `README_ANALYZER.md`
- **Want overview?** → Read `PROJECT_SUMMARY.md`
- **Having issues?** → Run `python verify_setup.py`

---

## 🔒 Security Notes

✅ Template uses placeholders (not real credentials)  
⚠️ **Never commit config.py to version control**  
⚠️ Use Demo account for testing first  

---

## 📈 What It Does

1. **Connects** to Capital.com API (Demo or Live)
2. **Fetches** all markets by category:
   - Commodities (Gold, Oil, Silver...)
   - Forex (EUR/USD, GBP/USD...)
   - Indices (S&P 500, NASDAQ...)
   - Cryptocurrencies (Bitcoin, Ethereum...)
   - Shares/ETFs (Apple, Tesla...)
3. **Calculates** performance for each time period
4. **Exports** to CSV with all metrics
5. **Displays** summary and top/bottom performers

---

## ⏱️ Execution Time

- **Quick test** (20 markets/category): ~2-5 minutes
- **Full analysis** (all markets): ~15-30 minutes
- Depends on: Number of markets, API response time, rate limiting

---

## 🛠️ Technical Stack

- **Language**: Python 3.7+
- **Dependencies**: requests, python-dateutil
- **API**: Capital.com REST API v1
- **Output**: CSV (Excel compatible)

---

## 💡 Tips

1. **Start with Demo**: Set `USE_DEMO = True` in config.py
2. **Test with limits**: Use `MAX_MARKETS_PER_CATEGORY = 10`
3. **Verify setup**: Run `verify_setup.py` before main script
4. **Quick view**: Use `view_results.py` to see top performers

---

## 📞 Support

- **API Docs**: https://capital.com/api
- **API Support**: support@capital.com
- **API FAQ**: https://capital.zendesk.com/hc/en-us/sections/4415178206354-API

---

## ✨ Ready to Use!

Everything is set up. Just:
1. Add your credentials to `config.py`
2. Run `python run_analyzer.py`
3. Open `capital_markets_analysis.csv`

Happy analyzing! 📊
