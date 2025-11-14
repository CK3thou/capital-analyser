"""Simplified test of the run_analyzer logic"""
from capital_analyzer import CapitalAPI
import config

# Initialize API client
api = CapitalAPI(
    api_key=config.API_KEY,
    identifier=config.USERNAME,
    password=config.PASSWORD,
    demo=config.USE_DEMO
)

# Create session
if not api.create_session():
    print("Failed to create session")
    exit(1)

print(f"\nSession info:")
print(f"  CST: {api.cst[:30]}...")
print(f"  Token: {api.security_token[:30]}...")
print(f"  Base URL: {api.base_url}")

# Test single category
print("\nTesting commodities...")
markets = api.get_markets_by_category('commodities', limit=1000)
print(f"Returned: {len(markets)} markets\n")

if markets:
    # Try to process first market
    market = markets[0]
    epic = market.get('epic')
    name = market.get('instrumentName', epic)
    print(f"First market: {name} ({epic})")
    
    # Get details
    details = api.get_market_details(epic)
    if details:
        print("✓ Got details successfully")
        snapshot = details.get('snapshot', {})
        print(f"  Bid: {snapshot.get('bid')}")
        print(f"  Offer: {snapshot.get('offer')}")
    else:
        print("✗ Could not get details")
