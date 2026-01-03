"""
Test script for Publix direct scraper

This will test scraping Publix stores directly from their website.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.services.scraper import PublixScraper
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_scraper(state: str = "KY"):
    """Test the Publix scraper"""
    print(f"=== Testing Publix Scraper for {state} ===\n")

    scraper = PublixScraper()

    try:
        print("Scraping Publix stores...")
        stores = scraper.scrape_stores(state=state)

        print(f"\n✅ Found {len(stores)} stores\n")

        if stores:
            print("Sample stores:")
            for i, store in enumerate(stores[:5], 1):
                print(f"\n{i}. Store #{store.get('store_number', 'N/A')}")
                print(f"   Address: {store.get('address', 'N/A')}")
                print(
                    f"   City: {store.get('city', 'N/A')}, {store.get('state', 'N/A')}"
                )
                print(f"   Zip: {store.get('zip_code', 'N/A')}")
                if store.get("latitude") and store.get("longitude"):
                    print(f"   Location: {store['latitude']}, {store['longitude']}")
        else:
            print("\n⚠️  No stores found. This could mean:")
            print("   1. Publix website structure changed")
            print("   2. Need to install ChromeDriver for Selenium")
            print("   3. Website requires JavaScript (use Selenium)")
            print("\nTo install ChromeDriver:")
            print("   macOS: brew install chromedriver")
            print("   Linux: sudo apt-get install chromium-chromedriver")
            print("   Or download from: https://chromedriver.chromium.org/")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        logger.exception("Scraper test failed")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Test Publix scraper")
    parser.add_argument("--state", default="KY", help="State code to scrape")

    args = parser.parse_args()
    test_scraper(args.state)
