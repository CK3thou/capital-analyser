"""
Test script to discover correct market navigation node IDs
"""

import requests
import config
from capital_analyzer import CapitalAPI

# Initialize API
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

print("Session created successfully!\n")

# Get top-level nodes
url = f"{api.base_url}/marketnavigation"
headers = api._get_auth_headers()

print("Fetching top-level market categories...")
response = requests.get(url, headers=headers)

if response.status_code == 200:
    data = response.json()
    nodes = data.get('nodes', [])
    
    print(f"\n✓ Found {len(nodes)} top-level categories:\n")
    print(f"{'ID':<40} {'Name':<30}")
    print("-" * 70)
    
    for node in nodes:
        node_id = node.get('id', '')
        name = node.get('name', '')
        print(f"{node_id:<40} {name:<30}")
    
    # Try to get markets from first few nodes
    print("\n" + "="*70)
    print("Checking which nodes contain markets...")
    print("="*70)
    
    for node in nodes[:10]:  # Check first 10
        node_id = node.get('id', '')
        name = node.get('name', '')
        
        url = f"{api.base_url}/marketnavigation/{node_id}"
        response = requests.get(url, headers=headers, params={"limit": 5})
        
        if response.status_code == 200:
            data = response.json()
            markets = data.get('markets', [])
            sub_nodes = data.get('nodes', [])
            
            if markets:
                print(f"\n✓ {name} ({node_id})")
                print(f"  Contains {len(markets)} markets (showing first 5)")
                for market in markets[:3]:
                    print(f"    - {market.get('instrumentName', '')} ({market.get('epic', '')})")
            
            if sub_nodes:
                print(f"\n  Has {len(sub_nodes)} sub-categories:")
                for sub in sub_nodes[:5]:
                    print(f"    - {sub.get('name', '')}")
        
else:
    print(f"Failed to fetch categories: {response.status_code}")
    print(f"Response: {response.text}")
