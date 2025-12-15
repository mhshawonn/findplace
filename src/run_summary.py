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
    parser.add_argument("--input", required=True, help="Input file containing URLs (CSV)")
    parser.add_argument("--output", required=True, help="Output CSV file")
    
    args = parser.parse_args()
    
    summarizer = WebsiteSummarizer()
    processed_rows = []
    fieldnames = []
    
    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            # First, detect the header
            sample = f.read(1024)
            f.seek(0)
            has_header = csv.Sniffer().has_header(sample)
            
            if has_header:
                reader = csv.DictReader(f)
                fieldnames = list(reader.fieldnames) if reader.fieldnames else []
                
                # Find the URL column
                url_col = None
                candidates = ["website", "url", "link", "homepage"]
                
                # 1. Exact match
                for col in fieldnames:
                    if col.lower() in candidates:
                        url_col = col
                        break
                
                # 2. Contains match if no exact match
                if not url_col:
                    for col in fieldnames:
                        for cand in candidates:
                            if cand in col.lower():
                                url_col = col
                                break
                        if url_col: break
                
                if not url_col:
                    logging.error(f"Could not find a URL column (looked for {candidates}). Please rename the column in your CSV.")
                    return

                logging.info(f"Using '{url_col}' as the URL source.")
                
                # Add Summary to fieldnames if not present
                if "Summary" not in fieldnames:
                    fieldnames.append("Summary")
                
                rows = list(reader)
                logging.info(f"Found {len(rows)} rows to process.")

                for i, row in enumerate(rows):
                    url = row.get(url_col)
                    if url and url.startswith("http"):
                        logging.info(f"Processing ({i+1}/{len(rows)}): {url}")
                        summary = summarizer.summarize_url(url)
                        row["Summary"] = summary
                    else:
                        logging.warning(f"Skipping row {i+1}: Invalid URL '{url}'")
                        row["Summary"] = ""
                    processed_rows.append(row)
            
            else:
                logging.error("Input CSV must have a header row.")
                return

    except Exception as e:
        logging.error(f"Error reading input file: {e}")
        return

    # Write output
    try:
        with open(args.output, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(processed_rows)
        logging.info(f"Saved extended results to {args.output}")
    except Exception as e:
        logging.error(f"Error writing output: {e}")

if __name__ == "__main__":
    main()
