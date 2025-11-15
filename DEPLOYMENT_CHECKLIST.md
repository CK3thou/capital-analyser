# ✅ Streamlit Deployment Checklist

## Pre-Deployment (Local)

- [ ] Run `python run_analyzer.py` to generate CSV data
- [ ] Verify `capital_markets_analysis.csv` exists and has data
- [ ] Test locally: `streamlit run streamlit_app.py`
- [ ] App loads without "No data available" message
- [ ] Filters and search work correctly
- [ ] Charts display properly

## GitHub Setup

- [ ] All changes committed to `main` branch
  ```bash
  git add .
  git commit -m "Add Streamlit app"
  git push origin main
  ```
- [ ] `capital_markets_analysis.csv` is committed (for initial data)
- [ ] `.streamlit/config.toml` is present
- [ ] `requirements.txt` includes streamlit, plotly, pandas

## Streamlit Cloud Deployment

- [ ] Have a GitHub account with this repo
- [ ] Have a Streamlit Cloud account (free at https://share.streamlit.io)
- [ ] Click "New app" on Streamlit Cloud
- [ ] Select:
  - Repository: `CK3thou/capital-analyser`
  - Branch: `main`
  - Main file path: `streamlit_app.py`
- [ ] Click "Deploy"
- [ ] Wait for deployment (usually 1-2 minutes)
- [ ] App appears at: `https://share.streamlit.io/<your-username>/capital-analyser`

## Post-Deployment (Cloud)

- [ ] App loads without errors
- [ ] Dashboard shows market data
- [ ] Search/filter functionality works
- [ ] Charts render correctly
- [ ] **OPTIONAL**: Add secrets for live data updates:
  - Go to app settings ⚙️
  - Click "Secrets"
  - Add your Capital.com API credentials
  - This allows the app to fetch fresh data

## Updating Data on Deployed App

### Method 1: Manual Update (Recommended)
```bash
# Fetch new data
python run_analyzer.py

# Commit and push
git add capital_markets_analysis.csv
git commit -m "Update market data"
git push origin main

# Streamlit Cloud auto-updates within seconds
```

### Method 2: Scheduled Updates (Advanced)
Create `.github/workflows/update-data.yml` to automatically:
- Run analyzer on a schedule
- Commit results back to repo
- Trigger Streamlit Cloud redeploy

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "No data available" | Run `python run_analyzer.py` and commit CSV |
| App won't deploy | Check `requirements.txt` has all dependencies |
| Charts blank | Ensure CSV has data and columns match code |
| Slow to load | CSV is large, normal. Add `@st.cache_data` |
| Secrets not working | Add them in Cloud dashboard, not `.streamlit/secrets.toml` |

## Share Your App

Once deployed, share the public URL:
```
https://share.streamlit.io/<your-username>/capital-analyser
```

Anyone can access it without installation!

## Performance Notes

- CSV loads once per session (cached with `@st.cache_data`)
- Filter/search updates instantly
- Charts update in real-time as you filter
- First load may take 10-15 seconds (normal for Streamlit Cloud)

## Useful Commands

```bash
# Test locally
streamlit run streamlit_app.py

# Run with specific port
streamlit run streamlit_app.py --server.port 8502

# Run in headless mode (no browser)
streamlit run streamlit_app.py --headless

# Clear cache
streamlit cache clear

# View config
streamlit config show
```

## Environment Variables

For Streamlit Cloud, use **Secrets**, not environment variables:
- ❌ Don't use `.env` files
- ✅ Use Streamlit Cloud "Secrets" in dashboard
- ✅ Access via `st.secrets.get("KEY_NAME")`

## Questions?

- 📚 Check `STREAMLIT_DEPLOYMENT.md` for detailed setup
- 📖 See `STREAMLIT_FIX.md` for full explanation
- 🎯 View `README.md` for project overview
