"""
Test Google Places API scraper

Make sure GOOGLE_PLACES_API_KEY is set in backend/.env
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "backend", ".env"))

from app.services.scraper_google_places import PublixScraperGooglePlaces
import logging

logging.basicConfig(level=logging.INFO)


def test_google_places(state: str = "FL"):
    """Test Google Places scraper"""
    print(f"=== Testing Google Places API for {state} ===\n")

    api_key = os.getenv("GOOGLE_PLACES_API_KEY")
    if not api_key:
        print("❌ ERROR: GOOGLE_PLACES_API_KEY not found in environment")
        print("\nTo fix:")
        print("1. Get API key: https://console.cloud.google.com/")
        print("2. Enable 'Places API'")
        print("3. Add to backend/.env: GOOGLE_PLACES_API_KEY=your_key")
        return

    print(f"✅ API Key found: {api_key[:10]}...\n")

    try:
        scraper = PublixScraperGooglePlaces()
        print(f"Searching for Publix stores in {state}...\n")

        stores = scraper.scrape_stores(state=state)

        print(f"✅ Found {len(stores)} stores!\n")

        if stores:
            print("Sample stores:")
            for i, store in enumerate(stores[:5], 1):
                print(f"\n{i}. {store.get('city', 'N/A')}, {store.get('state', 'N/A')}")
                print(f"   Address: {store.get('address', 'N/A')}")
                print(
                    f"   Location: {store.get('latitude', 'N/A')}, {store.get('longitude', 'N/A')}"
                )
        else:
            print("⚠️  No stores found. Check:")
            print("   - API key is valid")
            print("   - Places API is enabled in Google Cloud Console")
            print("   - Billing is enabled (free tier is fine)")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--state", default="FL", help="State to search (e.g., FL, GA)")
    args = parser.parse_args()
    test_google_places(args.state)
