import argparse
import logging
import json
import pandas as pd
import os
from src.scraper import Scraper
from src.utils.map_gen import MapGenerator

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def main():
    setup_logging()
    
    parser = argparse.ArgumentParser(description="OpenStreetMap Business Scraper")
    parser.add_argument("--terms", nargs="+", required=True, help="List of search terms (e.g. cafe restaurant)")
    parser.add_argument("--location", required=True, help="Location name (e.g. 'New York City')")
    parser.add_argument("--enrich", action="store_true", help="Enable website enrichment (crawling)")
    parser.add_argument("--output", default="output", help="Output directory")
    
    args = parser.parse_args()
    
    print(f"Starting scrape for {args.terms} in {args.location}...")
    
    scraper = Scraper(enrich=args.enrich)
    results = scraper.scrape(args.terms, args.location)
    
    if not results:
        print("No results found.")
        return

    # Ensure output dir
    os.makedirs(args.output, exist_ok=True)
    
    # Save JSON
    json_path = os.path.join(args.output, "results.json")
    with open(json_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Saved {len(results)} results to {json_path}")
    
    # Save CSV
    # Flatten tags for CSV
    df = pd.json_normalize(results)
    csv_path = os.path.join(args.output, "results.csv")
    df.to_csv(csv_path, index=False)
    print(f"Saved CSV to {csv_path}")
    
    # Generate Map
    # Calculate center from results or use first one
    if results:
        center_lat = results[0]["lat"]
        center_lon = results[0]["lon"]
        map_path = os.path.join(args.output, "map.html")
        MapGenerator.generate_map(results, center_lat, center_lon, map_path)

if __name__ == "__main__":
    main()
