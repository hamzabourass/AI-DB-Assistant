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
            "foreign_keys": f"{self.base_url}/foreign_keys"
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
        # This would normally be another endpoint, but we'll mock it for now
        # In a real implementation, you'd call a specific endpoint for columns
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
            url = self.endpoints[endpoint_key]
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                # Extract the actual items - adjust based on the actual response structure
                items = data.get("items", [])
                
                # Update cache
                self.cache[endpoint_key] = items
                self.last_fetched[endpoint_key] = current_time
                
                return items
            else:
                print(f"Error fetching {endpoint_key}: {response.status_code}")
                # Return cached data if available, or empty list
                return self.cache.get(endpoint_key, [])
        
        except Exception as e:
            print(f"Exception fetching {endpoint_key}: {e}")
            # Return cached data if available, or empty list
            return self.cache.get(endpoint_key, [])