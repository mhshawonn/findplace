from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from src.scraper import Scraper
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="FindPlace API")

# Allow CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev only, restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScrapeRequest(BaseModel):
    terms: List[str]
    location: str
    enrich: bool = False

@app.post("/api/scrape")
async def scrape_businesses(request: ScrapeRequest):
    try:
        scraper = Scraper(enrich=request.enrich)
        results = scraper.scrape(request.terms, request.location)
        return {"count": len(results), "results": results}
    except Exception as e:
        logging.error(f"Error during scrape: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "ok"}
