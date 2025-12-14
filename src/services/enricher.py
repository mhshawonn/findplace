import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from typing import Dict, Any, Set
import logging

class EnrichmentService:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (compatible; FindPlaceBot/1.0; +http://example.com/bot)"
        }
        self.social_domains = {
            "facebook.com", "instagram.com", "twitter.com", "linkedin.com", "yelp.com", "tripadvisor.com"
        }

    def extract_emails(self, text: str) -> Set[str]:
        # Basic email regex
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        return set(re.findall(email_pattern, text))

    def extract_socials(self, soup: BeautifulSoup, base_url: str) -> Dict[str, str]:
        socials = {}
        for a in soup.find_all('a', href=True):
            href = a['href']
            full_url = urljoin(base_url, href)
            parsed = urlparse(full_url)
            domain = parsed.netloc.lower()
            
            # Remove www.
            if domain.startswith("www."):
                domain = domain[4:]
                
            if domain in self.social_domains:
                # Store the first link found for each network
                key = domain.split('.')[0]
                if key not in socials:
                    socials[key] = full_url
        return socials

    def enrich_business(self, business: Dict[str, Any]) -> Dict[str, Any]:
        website = business.get("website") or business.get("contact:website")
        if not website:
            return business
            
        # Ensure http/https
        if not website.startswith("http"):
            website = "http://" + website
            
        try:
            logging.info(f"Crawling {website}...")
            response = requests.get(website, headers=self.headers, timeout=5)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract Emails
            emails = self.extract_emails(soup.get_text())
            # Search in mailto links specifically
            for a in soup.find_all('a', href=True):
                if a['href'].startswith('mailto:'):
                    emails.add(a['href'][7:])
            
            business["extracted_emails"] = list(emails)
            
            # Extract Socials
            socials = self.extract_socials(soup, website)
            business.update(socials)
            
            # Extract Meta Description (sometimes useful for description)
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc and meta_desc.get('content'):
                business["meta_description"] = meta_desc['content']

        except Exception as e:
            logging.warning(f"Failed to crawl {website}: {e}")
            business["enrichment_error"] = str(e)
            
        return business
