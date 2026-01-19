# Copilot Instructions for Capital.com Market Analyzer

## Project Overview

**Capital.com Market Analyzer** is a Python application that fetches financial market data from Capital.com's REST API, analyzes performance metrics across multiple time periods, and displays results through multiple interfaces (Flask web, Streamlit dashboard, or CSV export).

**Core Purpose**: Aggregate market data (commodities, forex, indices, crypto, shares) with standardized performance calculations (1W, 1M, 3M, 6M, YTD, 1Y, 5Y, 10Y) for analysis and visualization.

## Architecture & Data Flow

### Three-Tier Architecture

1. **API Client Layer** (`capital_analyzer.py`)
   - `CapitalAPI` class manages session lifecycle with Capital.com
   - Handles authentication, session expiry (10-min timeout), and keep-alive pings
   - Methods organized by market category using `CATEGORY_NODE_IDS` map
   - Returns raw market and price data; **does NOT calculate performance**

2. **Processing Layer** (`run_analyzer.py`)
   - Orchestrates data fetching across all categories
   - Calculates performance metrics using historical price data
   - Stores results in SQLite DB and CSV (primary formats)
   - Implements rate limiting (0.15s between requests, ~10 req/sec API limit)

3. **Presentation Layer** (Multiple)
   - **Flask (`web_viewer.py`)**: Simple HTTP server, loads CSV, serves HTML+API
   - **Streamlit (`streamlit_app.py`)**: Interactive dashboard with filters, charts, sorting
   - **CSV**: Direct export for Excel/analysis tools
   - **Terminal (`view_results.py`)**: Quick tabular summary

### Data Flow Sequence

```
Capital.com API → CapitalAPI (authenticate, fetch) 
  → Calculate perf metrics (historical prices vs. current)
  → Store in SQLite + Export CSV
  → Web/Streamlit UI reads CSV (not live DB queries)
```

**Key Pattern**: CSV is the source of truth for web interfaces; database is optional backup.

## Critical Dependencies & Configuration

### Required Credentials (config.py)
- `API_KEY`, `USERNAME`, `PASSWORD`: Capital.com account credentials
- `USE_DEMO` (bool): Switch between demo API (testing) and live API (production)
- `CATEGORIES` (list): Filter which market types to fetch
- `OUTPUT_FILENAME` (str): CSV export path (default: `capital_markets_analysis.csv`)

### Performance Metric Calculation

All metrics follow the same formula: **`((current_price - historical_price) / historical_price) * 100`**

**Concrete Example:**
```
Current BTC price: $100,000
Price 1 week ago: $95,000
Performance = ((100,000 - 95,000) / 95,000) * 100 = 5.26%

Current Gold price: $2,000
Price 6 months ago: $2,200
Performance = ((2,000 - 2,200) / 2,200) * 100 = -9.09%
```

**Key Behaviors:**
- **Current Price**: Retrieved from market snapshot (`details['snapshot']['bid']`)
- **Historical Prices**: Fetched from API for specific dates using day-ago calculation:
  - 1W: `now - 7 days`
  - 1M: `now - 30 days`
  - 3M: `now - 90 days`
  - 6M: `now - 180 days`
  - YTD: `now - days_since_jan_1`
  - 1Y: `now - 365 days`
  - 5Y: `now - 1825 days`
  - 10Y: `now - 3650 days`
- **Missing Data**: Returns `None` (rendered as "N/A" in UI) when historical price unavailable
- **Validation**: Checks `old_price > 0` before division to prevent errors with invalid data
- **Snapshot Data**: `price_change_pct` comes directly from market snapshot, not calculated

## Common Workflows

### Run Data Fetch & Analysis
```bash
python run_analyzer.py
```
- Creates/updates database
- Generates `capital_markets_analysis.csv`
- Auto-opens web browser if configured

### View Results
```bash
python view_results.py  # Terminal summary
# OR
python web_viewer.py    # HTTP server on :5000
# OR
streamlit run streamlit_app.py  # Interactive dashboard
```

### Debug API Issues
Use `debug_api.py` to test authentication and individual API calls before running full analysis.

## Code Patterns & Conventions

### Performance Calculation Walkthrough

The `calculate_performance()` method in `capital_analyzer.py` executes this sequence:

1. **Fetch Current Market Data**
   ```python
   details = self.get_market_details(epic)  # HTTP GET /markets/{epic}
   current_price = details['snapshot']['bid']
   price_change_pct = details['snapshot']['percentageChange']  # Today's change
   ```

2. **For Each Time Period (1W, 1M, 3M, etc.)**
   - Calculate target date: `target_date = now - timedelta(days=days_ago)`
   - Query historical prices: `get_historical_prices(epic, from_date, to_date)`
   - Extract close price from response: `prices[0]['closePrice']['bid']`
   - Calculate: `((current - historical) / historical) * 100`

3. **Handle Missing Data**
   ```python
   if old_price and old_price > 0:  # Guard against None/zero
       performance['perf_1w'] = ((current_price - old_price) / old_price) * 100
   else:
       performance['perf_1w'] = None  # Returns None if data unavailable
   ```

**Real Code Flow:**
```python
# From run_analyzer.py - how results flow to CSV
for symbol in markets:
    perf = api.calculate_performance(symbol['epic'])
    csv_row = {
        'Symbol': symbol['symbol'],
        'Perf % 1W': format_percentage(perf['perf_1w']),  # "5.26%" or "N/A"
        'Perf % 1Y': format_percentage(perf['perf_1y']),
        ...
    }
```

### Session Management
```python
# Always check session validity before API calls
api.ensure_session()  # Auto-renews if expired
api.ping()            # Keep-alive every ~20 requests
```
Session tokens stored in headers: `CST` and `X-SECURITY-TOKEN`.

### Error Handling
- Network errors → logged, analysis continues for other categories
- API 429 (rate limit) → respect `Retry-After` header, use backoff
- Missing historical data → skip metric calculation, return "N/A"

### Rate Limiting
- 0.15s delay between requests (configurable in config.py)
- Capital.com API limit: ~10 requests/second (enforced)
- Auto-ping every 20 requests to prevent session timeout

### Category Mapping
`CATEGORY_NODE_IDS` dict maps category names to Capital.com API node identifiers:
- `commodities` → `hierarchy_v1.commodities_group`
- `forex`, `indices`, `cryptocurrencies`, `shares`, `etf` (similar pattern)

Do NOT hardcode these; use the dict for maintainability.

### Percentage Formatting
- Always format with 2 decimal places: `f"{value:.2f}%"`
- Handle None/NaN gracefully (return "N/A")
- Streamlit: use `parse_percentage()` to convert string percentages to float for charts

## Key File Responsibilities

| File | Role | Key Functions |
|------|------|---|
| `capital_analyzer.py` | API client | `create_session()`, `fetch_markets()`, `get_price_history()`, `calculate_performance()` |
| `run_analyzer.py` | Main orchestrator | `init_database()`, `fetch_and_analyze()`, fetches all categories, exports CSV |
| `web_viewer.py` | Flask HTTP server | `/api/markets`, `/api/categories` endpoints, renders `templates/index.html` |
| `streamlit_app.py` | Interactive dashboard | Load CSV, filtering, charts (plotly), real-time search |
| `config_template.py` | Configuration schema | Source of truth for all configurable settings |
| `view_results.py` | Terminal viewer | Reads CSV, displays stats and top/bottom performers |

## Testing & Validation

- **`minimal_test.py`**, **`simple_test.py`**: Basic API connection tests
- **`test_fetch.py`**: Fetch single market test
- **`verify_setup.py`**: Pre-flight checks (credentials, network, dependencies)

Run `verify_setup.py` before full analysis to catch config issues early.

## Important Gotchas

### Performance Calculation Edge Cases

**Case 1: New Asset (No 5Y/10Y data)**
```
Bitcoin (introduced 2009) - accessed 2025
- 1W: $45,000 → $48,000 = +6.67% ✓
- 5Y: Data available from 2020 ✓
- 10Y: Data unavailable → None = "N/A" in UI
```

**Case 2: Zero or Negative Historical Price**
```python
# API occasionally returns bad historical data
# Guard prevents division errors:
if old_price and old_price > 0:
    performance['perf_1w'] = ((current - old_price) / old_price) * 100
else:
    performance['perf_1w'] = None  # Safety fallback
```

**Case 3: YTD Calculation (Variable Days)**
```python
# Today: Dec 29, 2025
# YTD days = (Dec 29 - Jan 1) = 362 days
ytd_days = (now - datetime(now.year, 1, 1)).days
old_price = get_price_at_datetime(days_ago=362)
```

### Other Gotchas

1. **CSV is the source of truth**: Web/Streamlit read CSV, not live from API. Stale data if CSV not regenerated.
2. **Demo vs. Live**: Verify `USE_DEMO` config before fetching—data differs between environments.
3. **Session expiry**: 10-minute timeout; long pauses between requests may require manual renewal.
4. **Historical data gaps**: New instruments may lack 5Y/10Y data; "N/A" is expected.
5. **Percentage parsing**: Streamlit receives strings from CSV; use `parse_percentage()` for numeric operations.

## When Modifying

- **Adding metrics**: Update `CapitalAPI.calculate_performance()`, `run_analyzer.py` database schema, CSV export, and all three UIs (Flask, Streamlit, terminal).
- **Changing API endpoints**: Check Capital.com docs; node IDs in `CATEGORY_NODE_IDS` may shift.
- **Database schema changes**: Update `init_database()` AND existing migration logic if DB already exists.
- **UI styling**: Streamlit uses `st.markdown()` for CSS; Flask templates in `templates/index.html`.

---

**Last Updated**: 2025-12-29  
**Python Version**: 3.8+  
**Core Dependencies**: requests, pandas, flask, streamlit, plotly, python-dateutil
