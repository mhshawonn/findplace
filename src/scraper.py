import logging
import pandas as pd
from typing import List, Dict, Any
from .services.nominatim import NominatimService
from .services.overpass import OverpassService
from .services.enricher import EnrichmentService
from .utils.geo import GeoUtils

class Scraper:
    def __init__(self, enrich: bool = True):
        self.nominatim = NominatimService()
        self.overpass = OverpassService()
        self.enricher = EnrichmentService()
        self.should_enrich = enrich
        
    def scrape(self, search_terms: List[str], location: str) -> List[Dict[str, Any]]:
        logging.info(f"Geocoding location: {location}")
        loc_data = self.nominatim.get_lat_lon_bbox(location)
        
        if not loc_data:
            logging.error("Location not found.")
            return []
            
        bbox = loc_data["boundingbox"] # [s, n, w, e]
        logging.info(f"Found location: {loc_data['display_name']} (BBox: {bbox})")
        
        # Check if tiling is needed
        tiles = [bbox]
        if GeoUtils.is_bbox_too_large(bbox, max_sq_degrees=0.1): # Strict tiling
            logging.info("Area too large, tiling...")
            # Simple 2x2 split for now, could be recursive
            tiles = GeoUtils.split_bbox(bbox, rows=2, cols=2)
            logging.info(f"Split into {len(tiles)} tiles.")

        # Prepare tags
        # Map search terms to broad OSM keys
        # For simplicity, we assume search_terms are values for "amenity", "shop", "office"
        # Ideally, we allow user to specify "amenity=cafe"
        # But per requirements: "categoryMap"
        # We'll just search common keys for the values
        query_tags = {
            "amenity": search_terms,
            "shop": search_terms,
            "office": search_terms,
            "tourism": search_terms,
            "leisure": search_terms
        }
        
        all_results = []
        seen_ids = set()
        
        for i, tile in enumerate(tiles):
            logging.info(f"Querying tile {i+1}/{len(tiles)}...")
            elements = self.overpass.fetch_data(tile, query_tags)
            logging.info(f"Got {len(elements)} elements from tile.")
            
            for el in elements:
                el_id = el.get("id")
                if el_id in seen_ids:
                    continue
                    
                seen_ids.add(el_id)
                # Parse
                tags = el.get("tags", {})
                name = tags.get("name")
                if not name:
                    continue # Skip unnamed
                
                lat = el.get("lat")
                lon = el.get("lon")
                
                # Handling 'way' elements (they have center due to 'out center')
                if not lat and "center" in el:
                    lat = el["center"].get("lat")
                    lon = el["center"].get("lon")
                
                business = {
                    "osm_id": el_id,
                    "name": name,
                    "lat": lat,
                    "lon": lon,
                    "type": el.get("type"),
                    "tags": tags, # Keep raw tags
                    
                    # Normalized fields
                    "phone": tags.get("phone") or tags.get("contact:phone"),
                    "website": tags.get("website") or tags.get("contact:website"),
                    "address_city": tags.get("addr:city"),
                    "address_street": tags.get("addr:street"),
                    "category": self._determine_category(tags, search_terms)
                }
                
                all_results.append(business)

        logging.info(f"Total unique businesses found: {len(all_results)}")
        
        # Enrichment
        if self.should_enrich:
            logging.info("Starting enrichment...")
            for b in all_results:
                self.enricher.enrich_business(b)
                
        return all_results

    def _determine_category(self, tags: Dict[str, str], search_terms: List[str]) -> str:
        # Match back to search term
        for k, v in tags.items():
            if v in search_terms:
                return v
        return "other"
