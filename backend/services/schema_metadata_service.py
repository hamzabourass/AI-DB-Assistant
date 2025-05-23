"""Service for fetching schema metadata from Oracle APEX endpoints."""
import requests
import json
from typing import Dict, List, Any, Optional

class SchemaMetadataService:
    """Service for fetching and caching schema metadata from Oracle APEX endpoints."""
    
    def __init__(self):
        """Initialize the schema metadata service."""
        self.base_url = "https://apex.oracle.com/pls/apex/ai_database_assistant/schema-metadata"
        self.endpoints = {
            "tables": f"{self.base_url}/tables",
            "views": f"{self.base_url}/views",
            "indexes": f"{self.base_url}/indexes",
            "foreign_keys": f"{self.base_url}/foreign_keys",
        }
        self.cache = {}  # Simple in-memory cache
        self.cache_ttl = 3600  # Cache time-to-live in seconds (1 hour)
        self.last_fetched = {}  # Timestamp of last fetch for each endpoint
    
    def fetch_tables(self) -> List[Dict[str, Any]]:
        """Fetch all tables metadata."""
        return self._fetch_endpoint("tables")
    
    def fetch_views(self) -> List[Dict[str, Any]]:
        """Fetch all views metadata."""
        return self._fetch_endpoint("views")
    
    def fetch_indexes(self) -> List[Dict[str, Any]]:
        """Fetch all indexes metadata."""
        return self._fetch_endpoint("indexes")
    
    def fetch_foreign_keys(self) -> List[Dict[str, Any]]:
        """Fetch all foreign keys metadata."""
        return self._fetch_endpoint("foreign_keys")
    
    def get_table_info(self, table_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific table."""
        tables = self.fetch_tables()
        for table in tables:
            if table.get("table_name", "").lower() == table_name.lower():
                return table
        return None
    
    def get_table_columns(self, table_name: str) -> List[Dict[str, Any]]:
        """Get columns for a specific table."""
        table = self.get_table_info(table_name)
        if table and "columns" in table:
            return table["columns"]
        return []
    
    def get_table_indexes(self, table_name: str) -> List[Dict[str, Any]]:
        """Get indexes for a specific table."""
        indexes = self.fetch_indexes()
        return [idx for idx in indexes if idx.get("table_name", "").lower() == table_name.lower()]
    
    def get_table_foreign_keys(self, table_name: str) -> List[Dict[str, Any]]:
        """Get foreign keys for a specific table."""
        fkeys = self.fetch_foreign_keys()
        return [fk for fk in fkeys if fk.get("table_name", "").lower() == table_name.lower()]
    
    def search_tables(self, search_term: str) -> List[Dict[str, Any]]:
        """Search for tables matching the search term."""
        tables = self.fetch_tables()
        search_term = search_term.lower()
        return [
            table for table in tables 
            if search_term in table.get("table_name", "").lower() or 
               search_term in table.get("comments", "").lower()
        ]
    
    def _fetch_endpoint(self, endpoint_key: str) -> List[Dict[str, Any]]:
        """Fetch data from a specific endpoint with caching."""
        import time
        current_time = time.time()
        
        # Check if we have a valid cached response
        if (endpoint_key in self.cache and 
            endpoint_key in self.last_fetched and
            current_time - self.last_fetched[endpoint_key] < self.cache_ttl):
            return self.cache[endpoint_key]
        
        # Fetch fresh data
        try:
            print(f"Fetching {endpoint_key}")
            url = self.endpoints[endpoint_key]
            print(f"url {url}")
            
            # Add headers that mimic a browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            }
            
            # Create a session to maintain cookies
            session = requests.Session()
            
            # Use a shorter timeout
            response = session.get(url, headers=headers, timeout=30)
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    # Update cache
                    # self.cache[endpoint_key] = response
                    # self.last_fetched[endpoint_key] = current_time
                    print(f"Successfully fetched {len(response) if isinstance(response, list) else 'data'}")
                    return response.text
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON response: {str(e)}")
                    print(f"Response content: {response.text[:100]}...")  # Print the first 100 chars
                    return self.cache.get(endpoint_key, [])
            else:
                print(f"Error fetching {endpoint_key}: {response.status_code}")
                print(f"Response content: {response.text[:100]}...")
                return self.cache.get(endpoint_key, [])
        
        except requests.exceptions.ConnectionError as e:
            print(f"Connection error fetching {endpoint_key}: {str(e)}")
            # Try to provide more specific error information
            if "RemoteDisconnected" in str(e):
                print("The server closed the connection unexpectedly. This could be due to:")
                print("- Server timing out the request")
                print("- Firewall or proxy issues")
                print("- Server rejecting the request format")
            return self.cache.get(endpoint_key, [])
            
        except requests.exceptions.Timeout:
            print(f"Request timed out for {endpoint_key}")
            return self.cache.get(endpoint_key, [])
            
        except Exception as e:
            print(f"Exception fetching {endpoint_key}: {e}")
            return self.cache.get(endpoint_key, [])