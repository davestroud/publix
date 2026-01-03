"""
Script to run data collection using the multi-agent system

This will use the Data Collector Agent to scrape and collect real data,
then you can run analyses to generate predictions.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.services.database import SessionLocal
from app.agents.data_collector import DataCollectorAgent
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def collect_data_for_region(state: str = "KY"):
    """Collect data for a region using the data collector agent"""
    db = SessionLocal()

    try:
        collector = DataCollectorAgent(db)

        print(f"=== Collecting data for {state} ===\n")

        # Collect Publix stores
        print("1. Collecting Publix stores...")
        try:
            stores = collector.collect_publix_stores(state=state)
            print(f"   ✓ Collected {len(stores)} Publix stores")
        except Exception as e:
            print(f"   ⚠️  Error collecting Publix stores: {e}")
            print(
                "   Note: Scraper may need implementation (see scraper_implementations.md)"
            )

        # Collect competitor stores
        print("\n2. Collecting competitor stores...")
        try:
            competitors = collector.collect_competitor_stores(state=state)
            total = sum(len(stores) for stores in competitors.values())
            print(f"   ✓ Collected {total} competitor stores")
            for name, stores in competitors.items():
                print(f"      - {name}: {len(stores)} stores")
        except Exception as e:
            print(f"   ⚠️  Error collecting competitor stores: {e}")

        # Collect demographics for major cities
        print("\n3. Collecting demographics...")
        cities = [
            {"city": "Lexington", "state": state},
            {"city": "Louisville", "state": state},
            {"city": "Bowling Green", "state": state},
            {"city": "Owensboro", "state": state},
        ]
        try:
            demographics = collector.collect_demographics(cities)
            print(f"   ✓ Collected demographics for {len(demographics)} cities")
        except Exception as e:
            print(f"   ⚠️  Error collecting demographics: {e}")
            print("   Note: Demographics service may need Census API key")

        # Collect zoning records
        print("\n4. Collecting zoning records...")
        try:
            zoning = collector.collect_zoning_records(
                cities, min_acreage=15.0, max_acreage=25.0
            )
            print(f"   ✓ Collected {len(zoning)} zoning records")
        except Exception as e:
            print(f"   ⚠️  Error collecting zoning records: {e}")
            print("   Note: Zoning scraper may need implementation")

        print("\n✅ Data collection complete!")
        print("\nNext steps:")
        print(
            "  1. Run analysis: curl -X POST http://localhost:8000/api/analyze -H 'Content-Type: application/json' -d '{\"region\": \""
            + state
            + "\"}'"
        )
        print("  2. Or use the Python client to run analysis")

    except Exception as e:
        logger.error(f"Error during data collection: {e}", exc_info=True)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Collect data using the multi-agent system"
    )
    parser.add_argument("--state", default="KY", help="State code to collect data for")

    args = parser.parse_args()
    collect_data_for_region(args.state)
