# Streamlit Deployment Guide

## Prerequisites
- GitHub account
- Streamlit Cloud account (free at https://streamlit.io/cloud)

## Setup Steps

### 1. Push to GitHub
```bash
git add .
git commit -m "Add Streamlit app"
git push origin main
```

### 2. Connect to Streamlit Cloud
1. Go to https://share.streamlit.io
2. Click **New app**
3. Select your repository: `capital-analyser`
4. Select main branch
5. Set main file path to: `streamlit_app.py`
6. Click **Deploy**

### 3. Add Secrets (for API credentials)
In Streamlit Cloud dashboard:
1. Go to your app settings (⚙️)
2. Click **Secrets**
3. Add:
```
API_KEY = "your-api-key"
USERNAME = "your-email"
PASSWORD = "your-password"
USE_DEMO = true
```

### 4. Update config.py (Optional)
The app can read from secrets:
```python
import streamlit as st

API_KEY = st.secrets.get("API_KEY", "your-api-key")
USERNAME = st.secrets.get("USERNAME", "your-email")
PASSWORD = st.secrets.get("PASSWORD", "your-password")
USE_DEMO = st.secrets.get("USE_DEMO", True)
```

## Architecture
- **streamlit_app.py** - Main Streamlit app (displays data from CSV)
- **run_analyzer.py** - Fetches data from Capital.com API (run locally or on schedule)
- **capital_markets_analysis.csv** - Data file (commit to repo for initial data)

## Note on Data
The Streamlit app displays data from `capital_markets_analysis.csv`. To update data:

### Option 1: Local Run + Git Push
```bash
python run_analyzer.py
git add capital_markets_analysis.csv
git commit -m "Update market data"
git push
```

### Option 2: Scheduled Tasks (GitHub Actions)
Create `.github/workflows/update-data.yml` to automatically run analyzer on schedule.

## Troubleshooting

### "No data available"
- Make sure `capital_markets_analysis.csv` exists in the repo
- Run `python run_analyzer.py` locally and commit the CSV

### Secrets not working
- Check Streamlit Cloud secrets are set correctly
- Use `st.secrets` to access them

### App won't load
- Check browser console for errors
- Verify all dependencies in `requirements.txt`
- Check Streamlit logs in Cloud dashboard
