"""Test the updated get_markets_by_category method"""
from capital_analyzer import CapitalAPI
import config

api = CapitalAPI(
    api_key=config.API_KEY,
    identifier=config.USERNAME,
    password=config.PASSWORD,
    demo=config.USE_DEMO
)

if not api.create_session():
    print("Session failed")
    exit(1)

print("Testing get_markets_by_category...\n")

# Test commodities
markets = api.get_markets_by_category('commodities', limit=10)
print(f"\nReturned {len(markets)} markets")

if markets:
    print("\nFirst 3 markets:")
    for i, market in enumerate(markets[:3], 1):
        print(f"  {i}. {market.get('instrumentName', 'N/A')} ({market.get('epic', 'N/A')})")
