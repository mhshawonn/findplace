import requests
import time
from typing import Optional, List, Dict, Any

class NominatimService:
    BASE_URL = "https://nominatim.openstreetmap.org/search"
    
    def __init__(self, user_agent: str = "FindPlace/1.0 (dev_test_app_v1@generic.com)"):
        self.headers = {"User-Agent": user_agent}
        self.last_request_time = 0
        self.min_delay = 1.1  # OSM Policy: Max 1 req/sec

    def _wait_for_rate_limit(self):
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_delay:
            time.sleep(self.min_delay - elapsed)
        self.last_request_time = time.time()

    def get_lat_lon_bbox(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Geocodes a query string to a location with bounding box.
        Returns a dict with 'lat', 'lon', 'display_name', 'boundingbox' key.
        boundingbox is [south, north, west, east] (strings).
        """
        self._wait_for_rate_limit()
        
        params = {
            "q": query,
            "format": "json",
            "polygon_geojson": 1,
            "limit": 1
        }
        
        try:
            response = requests.get(self.BASE_URL, params=params, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            if not data:
                return None
                
            result = data[0]
            # Nominatim returns bbox as [south, north, west, east] in string format
            return {
                "display_name": result.get("display_name"),
                "lat": float(result.get("lat")),
                "lon": float(result.get("lon")),
                "boundingbox": [float(x) for x in result.get("boundingbox")],
                "geojson": result.get("geojson"),
                "osm_id": result.get("osm_id")
            }
        except Exception as e:
            print(f"Error geocoding '{query}': {e}")
            return None
