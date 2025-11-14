"""Deep inspection of market navigation structure"""
import requests
from capital_analyzer import CapitalAPI
import config
import json

api = CapitalAPI(
    api_key=config.API_KEY,
    identifier=config.USERNAME,
    password=config.PASSWORD,
    demo=config.USE_DEMO
)

if not api.create_session():
    print("Session failed")
    exit(1)

def explore_node(node_id, depth=0, max_depth=3):
    """Recursively explore a node"""
    if depth > max_depth:
        return
    
    indent = "  " * depth
    url = f"{api.base_url}/marketnavigation/{node_id}"
    headers = api._get_auth_headers()
    
    response = requests.get(url, headers=headers, params={"limit": 5})
    if response.status_code != 200:
        print(f"{indent}✗ Failed: {response.status_code}")
        return
    
    data = response.json()
    nodes = data.get('nodes', [])
    markets = data.get('markets', [])
    
    print(f"{indent}Node: {node_id}")
    print(f"{indent}  Markets: {len(markets)}")
    print(f"{indent}  Sub-nodes: {len(nodes)}")
    
    if markets:
        for m in markets[:2]:
            print(f"{indent}    - {m.get('instrumentName', 'N/A')}")
    
    if depth < max_depth and nodes:
        for node in nodes[:2]:  # Explore first 2 sub-nodes
            explore_node(node['id'], depth + 1, max_depth)

print("Exploring Commodities structure:\n")
explore_node('hierarchy_v1.commodities_group', depth=0, max_depth=2)

print("\n" + "="*60)
print("\nExploring Forex structure:\n")
explore_node('hierarchy_v1.forex', depth=0, max_depth=2)
