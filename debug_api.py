"""Debug script to see actual API responses"""
import requests
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

print(f"Session created: CST={api.cst[:20]}...")
print(f"Security Token={api.security_token[:20]}...")
print(f"Base URL: {api.base_url}\n")

# Try fetching commodities
node_id = "hierarchy_v1.commodities_group"
url = f"{api.base_url}/marketnavigation/{node_id}"
headers = api._get_auth_headers()

print(f"Trying: {url}")
print(f"Headers: {headers}\n")

response = requests.get(url, headers=headers, params={"limit": 10})

print(f"Status Code: {response.status_code}")
print(f"Response Headers: {dict(response.headers)}")
print(f"\nResponse Body:")
print(response.text[:500])
