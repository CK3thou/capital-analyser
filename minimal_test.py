"""Minimal test matching run_analyzer flow"""
from capital_analyzer import CapitalAPI
import config

# Create API client
api = CapitalAPI(
    api_key=config.API_KEY,
    identifier=config.USERNAME,
    password=config.PASSWORD,
    demo=config.USE_DEMO
)

# Create session
print("Creating session...")
if not api.create_session():
    print("Session failed")
    exit(1)

print(f"Session created")
print(f"CST length: {len(api.cst) if api.cst else 0}")
print(f"Token length: {len(api.security_token) if api.security_token else 0}")

# Try get_markets_by_category
print("\nCalling get_markets_by_category with limit=100...")
markets = api.get_markets_by_category('commodities', limit=100)
print(f"Got {len(markets)} markets")

if len(markets) > 0:
    print(f"\nFirst market: {markets[0].get('instrumentName')}")
