import requests
import time
from typing import List, Dict, Any

class OverpassService:
    BASE_URL = "https://overpass-api.de/api/interpreter"
    
    def __init__(self, user_agent: str = "FindPlace/1.0 (dev_test_app_v1@generic.com)"):
        self.headers = {"User-Agent": user_agent}
        # Overpass has limits, but mainly query complexity. 
        # We put a small delay to be safe.
        self.last_request_time = 0 
        self.min_delay = 2.0

    def _wait_for_rate_limit(self):
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_delay:
            time.sleep(self.min_delay - elapsed)
        self.last_request_time = time.time()

    def build_query(self, bbox: List[float], tags: Dict[str, List[str]]) -> str:
        """
        Constructs an Overpass QL query.
        bbox: [south, north, west, east]
        tags: dict of {key: [val1, val2]} e.g. {"amenity": ["cafe", "restaurant"]}
        """
        # Overpass QL bbox format is (south, west, north, east)
        # Nominatim returns [south, north, west, east]
        # We need to map Nominatim -> Overpass
        s, n, w, e = bbox
        
        # Determine query components
        components = []
        
        for key, values in tags.items():
            for val in values:
                # Add node, way, relation for each tag
                # Using ~ for regex match if needed, but = is faster if exact
                # User req said "partital match", so maybe ~ is better or just list
                # For safety, let's use exact match or reg matching if value has special chars
                # Simple exact match for now: ["key"="value"]
                
                # If wildcard/regex is needed we can change this. 
                # Let's assume values are simple strings for now.
                query_str = f'["{key}"="{val}"]'
                components.append(f'node{query_str}({s},{w},{n},{e});')
                components.append(f'way{query_str}({s},{w},{n},{e});')
                components.append(f'relation{query_str}({s},{w},{n},{e});')

        query = f"""
        [out:json][timeout:60];
        (
            {''.join(components)}
        );
        out center;
        """
        return query

    def fetch_data(self, bbox: List[float], tags: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        self._wait_for_rate_limit()
        query = self.build_query(bbox, tags)
        
        try:
            response = requests.post(self.BASE_URL, data={"data": query}, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            return data.get("elements", [])
        except Exception as e:
            print(f"Error fetching Overpass data: {e}")
            return []
