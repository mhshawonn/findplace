# OpenStreetMap Business Scraper

A production-ready tool to extract business leads from OpenStreetMap, enriching them with email and social media data from their websites.

## Features
- **Free Sources**: Uses OpenStreetMap (Overpass API) and Nominatim.
- **Geocoding**: resolving city names to bounding boxes.
- **Enrichment**: Crawls business websites to find `mailto:` links and social profiles.
- **Visualization**: Generates an interactive Leaflet map.
- **Export**: JSON and CSV formats.
- **Privacy/Politeness**: Respects `robots.txt` (via standard libraries) and implements rate limiting for OSM services.

## Setup

1. **Prerequisites**: Python 3.9+
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the scraper from the command line:

```bash
python3 -m src.main --terms cafe restaurant --location "Soho, London" --enrich --output results
```

### Arguments
- `--terms`: List of business types to search for (e.g. `cafe`, `bar`, `restaurant`, `bakery`). Matches against OSM tags like `amenity`, `shop`, `office`.
- `--location`: The city or area name to search within.
- `--enrich`: (Optional) Flag to enable website crawling for contact info.
- `--output`: (Optional) Directory to save results (default: `output`).

## Output
- `results.json`: Raw JSON data.
- `results.csv`: CSV export suitable for spreadsheets.
- `map.html`: Interactive map.

## Structure
- `src/services`: Core logic for API interactions.
- `src/utils`: Helper functions for Geometry and Mapping.
- `src/scraper.py`: Main orchestration logic.

## License
MIT

## Web Interface

The project now includes a modern web interface (React + Vite) and a FastAPI backend.

### 1. Start the Backend API
```bash
python3 -m uvicorn src.app:app --reload
```
The API will run at `http://127.0.0.1:8000`.

### 2. Start the Frontend
**Prerequisities:** Node.js (v18+)

```bash
cd frontend
npm install
npm run dev
```
The frontend will run at `http://localhost:5173`.
# findplace
