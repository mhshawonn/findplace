import logging
import requests
from bs4 import BeautifulSoup
from transformers import pipeline
import torch

class WebsiteSummarizer:
    def __init__(self, model_name="facebook/bart-large-cnn"):
        self.logger = logging.getLogger(__name__)
        self.model_name = model_name
        self.summarizer = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; FindPlaceBot/1.0; +http://example.com)'
        }

    def _load_model(self):
        if not self.summarizer:
            self.logger.info(f"Loading summarization model: {self.model_name}...")
            # Use CPU by default to be safe, or check for MPS (Apple Silicon) if available
            device = -1
            if torch.backends.mps.is_available():
                device = "mps" 
            
            self.summarizer = pipeline("summarization", model=self.model_name, device=device)
            self.logger.info("Model loaded.")

    def fetch_text(self, url: str) -> str:
        try:
            self.logger.info(f"Fetching {url}...")
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
                
            text = soup.get_text()
            
            # Break into lines and remove leading/trailing space on each
            lines = (line.strip() for line in text.splitlines())
            # Break multi-headlines into a line each
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            # Drop blank lines
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text
        except Exception as e:
            self.logger.error(f"Failed to fetch {url}: {e}")
            return None

    def summarize_url(self, url: str) -> str:
        text = self.fetch_text(url)
        if not text:
            return "Failed to content"
        
        # Check if text is too short
        if len(text.split()) < 50:
            return f"Content too short to summarize: {text[:200]}..."

        self._load_model()
        
        try:
            # Truncate text to avoiding token limit issues (simple char limit for now)
            # BART model max position embeddings is usually 1024 tokens.
            # ~4000 chars is a safe upper bound for input.
            input_text = text[:4000] 
            
            self.logger.info(f"Summarizing {len(input_text)} characters...")
            summary = self.summarizer(input_text, max_length=130, min_length=30, do_sample=False)
            
            result = summary[0]['summary_text']
            self.logger.info("Summary generated.")
            return result
        except Exception as e:
            self.logger.error(f"Summarization failed: {e}")
            return f"Summarization error: {str(e)}"
