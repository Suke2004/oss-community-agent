# tools/scrape_tool.py
# This Python script handles web scraping using ScrapeGraphAI.

import os
import json
import argparse
from scrapegraphai.graphs import SmartScraperGraph
from dotenv import load_dotenv

def main():
    """
    Parses command-line arguments and runs the ScrapeGraphAI scraper.
    """
    # Load environment variables from .env file
    load_dotenv()

    # Set up command-line argument parser
    parser = argparse.ArgumentParser(description="Run ScrapeGraphAI for web scraping.")
    parser.add_argument("source", help="The URL of the website to scrape.")
    parser.add_argument("prompt", help="The natural language prompt for data extraction.")
    parser.add_argument("--output", help="The path to save the scraped data as a JSON file.", default="scraped_data.json")
    
    args = parser.parse_args()

    # ScrapeGraphAI configuration
    graph_config = {
        "llm": {
            "model": "groq/gemma-7b-it", # Replace with your preferred LLM
            "api_key": os.getenv("GROQ_API_KEY"), # Ensure your API key is in the .env file
            "temperature": 0,
        },
        "embeddings": {
            "model": "ollama/nomic-embed-text",
            "base_url": os.getenv("OLLAMA_URL"),
        },
        "headless": True, # Runs the browser in the background
    }

    # Create and run the scraping graph
    smart_scraper_graph = SmartScraperGraph(
        prompt=args.prompt,
        source=args.source,
        config=graph_config
    )
    
    try:
        result = smart_scraper_graph.run()
        
        # Save the result to a JSON file
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=4)
        
        print(f"Scraping completed successfully. Data saved to {args.output}")

    except Exception as e:
        print(f"An error occurred during scraping: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()