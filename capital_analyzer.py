"""
Capital.com Market Analyzer
Fetches and categorizes market symbols with performance metrics
"""

import requests
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json


class CapitalAPI:
    """Capital.com API client"""
    
    CATEGORY_NODE_IDS = {
        'commodities': 'hierarchy_v1.commodities_group',
        'forex': 'hierarchy_v1.forex',
        'indices': 'hierarchy_v1.indices_group',
        'cryptocurrencies': 'hierarchy_v1.crypto_currencies_group',
        'shares': 'hierarchy_v1.shares',
        'etf': 'hierarchy_v1.etf_group',
    }
    
    def __init__(self, api_key: str, identifier: str, password: str, demo: bool = True):
        """
        Initialize Capital.com API client
        
        Args:
            api_key: Your API key from Capital.com
            identifier: Your username/email
            password: Your password
            demo: Use demo environment (True) or live (False)
        """
        self.api_key = api_key
        self.identifier = identifier
        self.password = password
        self.base_url = (
            "https://demo-api-capital.backend-capital.com/api/v1" if demo 
            else "https://api-capital.backend-capital.com/api/v1"
        )
        self.cst = None
        self.security_token = None
        self.session_expiry = None
        
    def create_session(self) -> bool:
        """Create a new API session with retry logic"""
        url = f"{self.base_url}/session"
        headers = {
            "X-CAP-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "identifier": self.identifier,
            "password": self.password,
            "encryptedPassword": False
        }
        
        # Retry logic for temporary server issues
        max_retries = 3
        retry_delay = 5  # seconds
        
        for attempt in range(1, max_retries + 1):
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=10)
                
                if response.status_code == 200:
                    self.cst = response.headers.get('CST')
                    self.security_token = response.headers.get('X-SECURITY-TOKEN')
                    self.session_expiry = datetime.now() + timedelta(minutes=10)
                    print("[OK] Session created successfully")
                    return True
                elif response.status_code >= 500:
                    # Server error - retry
                    if attempt < max_retries:
                        print(f"[WARNING] Server error {response.status_code} (attempt {attempt}/{max_retries}). Retrying in {retry_delay}s...")
                        time.sleep(retry_delay)
                        continue
                    else:
                        print(f"[ERROR] Session creation failed after {max_retries} attempts: {response.status_code}")
                        print(f"Response: {response.text}")
                        return False
                else:
                    # Client error - don't retry
                    print(f"[ERROR] Session creation failed: {response.status_code}")
                    print(f"Response: {response.text}")
                    return False
            except requests.exceptions.Timeout:
                if attempt < max_retries:
                    print(f"[WARNING] Request timeout (attempt {attempt}/{max_retries}). Retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                    continue
                else:
                    print(f"[ERROR] Request timeout after {max_retries} attempts")
                    return False
            except Exception as e:
                if attempt < max_retries:
                    print(f"[WARNING] Error creating session: {str(e)} (attempt {attempt}/{max_retries}). Retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                    continue
                else:
                    print(f"[ERROR] Error creating session after {max_retries} attempts: {str(e)}")
                    return False
        
        return False
    
    def ensure_session(self):
        """Ensure we have a valid session, create if needed"""
        if not self.cst or not self.session_expiry or datetime.now() >= self.session_expiry:
            return self.create_session()
        return True
    
    def ping(self) -> bool:
        """Ping the service to keep session alive"""
        if not self.ensure_session():
            return False
            
        url = f"{self.base_url}/ping"
        headers = self._get_auth_headers()
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                self.session_expiry = datetime.now() + timedelta(minutes=10)
                return True
            return False
        except:
            return False
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for requests"""
        return {
            "X-SECURITY-TOKEN": self.security_token,
            "CST": self.cst,
            "Content-Type": "application/json"
        }
    
    def get_markets_by_category(self, category: str, limit: int = 100) -> List[Dict]:
        """
        Get all markets for a specific category by exploring the navigation hierarchy
        with retry logic for transient failures
        
        Args:
            category: One of 'commodities', 'forex', 'indices', 'cryptocurrencies', 'shares', 'etf'
            limit: Maximum number of results per sub-category (default 100, max supported by API)
        
        Returns:
            List of market dictionaries
        """
        if not self.ensure_session():
            return []
        
        node_id = self.CATEGORY_NODE_IDS.get(category.lower())
        if not node_id:
            print(f"[ERROR] Unknown category: {category}")
            return []
        
        all_markets = []
        headers = self._get_auth_headers()
        nodes_to_visit = [node_id]
        visited_nodes = set()
        
        max_retries = 3
        retry_delay = 2
        
        try:
            while nodes_to_visit:
                current_node = nodes_to_visit.pop(0)
                
                if current_node in visited_nodes:
                    continue
                visited_nodes.add(current_node)
                
                url = f"{self.base_url}/marketnavigation/{current_node}"
                
                # Retry logic for individual node fetches
                for attempt in range(1, max_retries + 1):
                    try:
                        response = requests.get(url, headers=headers, params={"limit": limit}, timeout=10)
                        
                        if response.status_code == 200:
                            data = response.json()
                            markets = data.get('markets', [])
                            sub_nodes = data.get('nodes', [])
                            
                            # Add markets from this node
                            if markets:
                                all_markets.extend(markets)
                            
                            # Add sub-nodes to visit queue
                            for sub_node in sub_nodes:
                                sub_id = sub_node.get('id')
                                if sub_id and sub_id not in visited_nodes:
                                    nodes_to_visit.append(sub_id)
                            break  # Success, move to next node
                        
                        elif response.status_code >= 500:
                            # Server error - retry
                            if attempt < max_retries:
                                print(f"[WARNING] Server error {response.status_code} fetching {current_node} (attempt {attempt}/{max_retries}). Retrying...")
                                time.sleep(retry_delay)
                                continue
                            else:
                                print(f"[WARNING] Skipping {current_node} after {max_retries} failed attempts")
                                break
                        else:
                            # Client error or other - skip this node
                            break
                    
                    except requests.exceptions.Timeout:
                        if attempt < max_retries:
                            print(f"[WARNING] Timeout fetching {current_node} (attempt {attempt}/{max_retries}). Retrying...")
                            time.sleep(retry_delay)
                            continue
                        else:
                            print(f"[WARNING] Skipping {current_node} after timeout")
                            break
                    
                    except Exception as e:
                        print(f"[WARNING] Error fetching {current_node}: {str(e)}")
                        break
                
                time.sleep(0.05)  # Rate limiting
            
            # Remove duplicates based on epic
            seen_epics = set()
            unique_markets = []
            for market in all_markets:
                epic = market.get('epic')
                if epic and epic not in seen_epics:
                    seen_epics.add(epic)
                    unique_markets.append(market)
            
            print(f"[OK] Found {len(unique_markets)} unique markets in {category}")
            return unique_markets
            
        except Exception as e:
            print(f"[ERROR] Error fetching {category}: {str(e)}")
            return []
    
    def get_market_details(self, epic: str) -> Optional[Dict]:
        """Get detailed information for a specific market with retry logic"""
        if not self.ensure_session():
            return None
        
        url = f"{self.base_url}/markets/{epic}"
        headers = self._get_auth_headers()
        
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(1, max_retries + 1):
            try:
                response = requests.get(url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    return response.json()
                
                elif response.status_code >= 500:
                    if attempt < max_retries:
                        time.sleep(retry_delay)
                        continue
                    else:
                        print(f"[WARNING] Could not fetch details for {epic} after {max_retries} attempts")
                        return None
                else:
                    return None
            
            except requests.exceptions.Timeout:
                if attempt < max_retries:
                    time.sleep(retry_delay)
                    continue
                else:
                    return None
            
            except Exception as e:
                return None
        
        return None
    
    def get_historical_prices(self, epic: str, resolution: str = "DAY", 
                            from_date: Optional[str] = None, 
                            to_date: Optional[str] = None,
                            max_points: int = 1000) -> Optional[Dict]:
        """
        Get historical prices for a market
        
        Args:
            epic: Market epic code
            resolution: MINUTE, MINUTE_5, MINUTE_15, MINUTE_30, HOUR, HOUR_4, DAY, WEEK
            from_date: Start date in ISO format (e.g., "2023-01-01T00:00:00")
            to_date: End date in ISO format
            max_points: Maximum number of data points
        
        Returns:
            Dictionary with price history or None
        """
        if not self.ensure_session():
            return None
        
        url = f"{self.base_url}/prices/{epic}"
        headers = self._get_auth_headers()
        params = {
            "resolution": resolution,
            "max": max_points
        }
        
        if from_date:
            params["from"] = from_date
        if to_date:
            params["to"] = to_date
        
        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                return response.json()
            return None
        except:
            return None
    
    def get_all_markets(self) -> List[Dict]:
        """Get all available markets (may take a while)"""
        all_markets = []
        
        for category in self.CATEGORY_NODE_IDS.keys():
            markets = self.get_markets_by_category(category)
            for market in markets:
                market['category'] = category
            all_markets.extend(markets)
            time.sleep(0.1)  # Rate limiting
        
        return all_markets
    
    def calculate_performance(self, epic: str) -> Dict[str, Optional[float]]:
        """
        Calculate performance metrics for a market
        
        Returns:
            Dictionary with performance percentages for various time periods
        """
        performance = {
            'price_change_pct': None,
            'perf_1w': None,
            'perf_1m': None,
            'perf_3m': None,
            'perf_6m': None,
            'perf_ytd': None,
            'perf_1y': None,
            'perf_5y': None,
            'perf_10y': None,
            'perf_all_time': None,
        }
        
        # Get current market snapshot first
        details = self.get_market_details(epic)
        if details and 'snapshot' in details:
            snapshot = details['snapshot']
            performance['price_change_pct'] = snapshot.get('percentageChange')
        
        # Calculate historical performance
        now = datetime.now()
        
        # Helper function to get price at a specific date
        def get_price_at_date(days_ago: int) -> Optional[float]:
            target_date = now - timedelta(days=days_ago)
            from_str = target_date.strftime("%Y-%m-%dT00:00:00")
            to_str = (target_date + timedelta(days=1)).strftime("%Y-%m-%dT00:00:00")
            
            prices = self.get_historical_prices(epic, resolution="DAY", 
                                               from_date=from_str, 
                                               to_date=to_str, 
                                               max_points=5)
            if prices and 'prices' in prices and len(prices['prices']) > 0:
                # Get the close price from the first available data point
                return prices['prices'][0].get('closePrice', {}).get('bid')
            return None
        
        # Get current price
        current_price = None
        if details and 'snapshot' in details:
            current_price = details['snapshot'].get('bid')
        
        if current_price:
            # 1 Week (7 days)
            old_price = get_price_at_date(7)
            if old_price and old_price > 0:
                performance['perf_1w'] = ((current_price - old_price) / old_price) * 100
            
            # 1 Month (30 days)
            old_price = get_price_at_date(30)
            if old_price and old_price > 0:
                performance['perf_1m'] = ((current_price - old_price) / old_price) * 100
            
            # 3 Months (90 days)
            old_price = get_price_at_date(90)
            if old_price and old_price > 0:
                performance['perf_3m'] = ((current_price - old_price) / old_price) * 100
            
            # 6 Months (180 days)
            old_price = get_price_at_date(180)
            if old_price and old_price > 0:
                performance['perf_6m'] = ((current_price - old_price) / old_price) * 100
            
            # YTD (from Jan 1st of current year)
            ytd_days = (now - datetime(now.year, 1, 1)).days
            old_price = get_price_at_date(ytd_days)
            if old_price and old_price > 0:
                performance['perf_ytd'] = ((current_price - old_price) / old_price) * 100
            
            # 1 Year (365 days)
            old_price = get_price_at_date(365)
            if old_price and old_price > 0:
                performance['perf_1y'] = ((current_price - old_price) / old_price) * 100
            
            # 5 Years (1825 days)
            old_price = get_price_at_date(1825)
            if old_price and old_price > 0:
                performance['perf_5y'] = ((current_price - old_price) / old_price) * 100
            
            # 10 Years (3650 days)
            old_price = get_price_at_date(3650)
            if old_price and old_price > 0:
                performance['perf_10y'] = ((current_price - old_price) / old_price) * 100
        
        return performance
