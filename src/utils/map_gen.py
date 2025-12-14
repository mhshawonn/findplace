import folium
from typing import List, Dict, Any
import os

class MapGenerator:
    @staticmethod
    def generate_map(businesses: List[Dict[str, Any]], center_lat: float, center_lon: float, output_path: str):
        """
        Generates a Leaflet map with markers for all businesses.
        """
        m = folium.Map(location=[center_lat, center_lon], zoom_start=14)
        
        for b in businesses:
            lat = b.get("lat")
            lon = b.get("lon")
            name = b.get("name", "Unknown Business")
            tags = b.get("tags", {})
            website = b.get("website") or b.get("contact:website")
            
            # Create popup content
            html = f"<b>{name}</b><br>"
            if website:
                html += f"<a href='{website}' target='_blank'>{website}</a><br>"
            
            # Add some tags to popup
            display_tags = ["amenity", "shop", "phone", "opening_hours"]
            for t in display_tags:
                if t in tags:
                    html += f"<b>{t}:</b> {tags[t]}<br>"
                elif t in b and b[t]: # if flat structure
                    html += f"<b>{t}:</b> {b[t]}<br>"

            if lat and lon:
                folium.Marker(
                    [lat, lon],
                    popup=folium.Popup(html, max_width=300),
                    tooltip=name
                ).add_to(m)
        
        # Create output directory if needed
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        m.save(output_path)
        print(f"Map saved to {output_path}")
