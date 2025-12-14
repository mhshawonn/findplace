import argparse
import csv
import logging
import sys
from src.services.summarizer import WebsiteSummarizer

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def main():
    setup_logging()
    
    parser = argparse.ArgumentParser(description="Generate AI summaries from a list of URLs")
    parser.add_argument("--input", required=True, help="Input file containing URLs (CSV or TXT)")
    parser.add_argument("--output", required=True, help="Output CSV file")
    
    args = parser.parse_args()
    
    urls = []
    
    # Detemine input type
    try:
        if args.input.endswith('.csv'):
            with open(args.input, 'r') as f:
                reader = csv.reader(f)
                # Assume URL is in the first column or look for header "website" or "url"
                headers = next(reader, None)
                url_idx = 0
                if headers:
                    # Try to find URL column
                    lower_headers = [h.lower() for h in headers]
                    if "website" in lower_headers:
                        url_idx = lower_headers.index("website")
                    elif "url" in lower_headers:
                        url_idx = lower_headers.index("url")
                    else:
                        # Reset file pointer if no header, or just accept first col
                        # For simplicity, if header doesn't look like URL, treat as data?
                        # Let's simple check if header looks like URL
                        if not headers[0].startswith("http"):
                             pass # Header row
                        else:
                             urls.append(headers[0]) # No header
                             
                for row in reader:
                    if row and len(row) > url_idx:
                        url = row[url_idx]
                        if url and url.startswith("http"):
                            urls.append(url)
        else:
            # Assume text file with one URL per line
            with open(args.input, 'r') as f:
                urls = [line.strip() for line in f if line.strip().startswith("http")]
                
    except Exception as e:
        logging.error(f"Error reading input file: {e}")
        return

    if not urls:
        logging.warning("No URLs found in input file.")
        return

    logging.info(f"Found {len(urls)} URLs to summarize.")
    
    summarizer = WebsiteSummarizer()
    results = []
    
    for i, url in enumerate(urls):
        logging.info(f"Processing ({i+1}/{len(urls)}): {url}")
        summary = summarizer.summarize_url(url)
        results.append({"URL": url, "Summary": summary})
        
    # Write output
    try:
        with open(args.output, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["URL", "Summary"])
            writer.writeheader()
            writer.writerows(results)
        logging.info(f"Saved results to {args.output}")
    except Exception as e:
        logging.error(f"Error writing output: {e}")

if __name__ == "__main__":
    main()
