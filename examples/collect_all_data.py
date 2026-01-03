"""
Comprehensive data collection script

Collects Publix stores, competitors, demographics, and zoning data
for all Publix states or specific states.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.services.database import SessionLocal
from app.agents.data_collector import DataCollectorAgent
import logging
from typing import List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Publix operates in these states
PUBLIX_STATES = [
    "FL",  # Florida (primary market)
    "GA",  # Georgia
    "AL",  # Alabama
    "SC",  # South Carolina
    "NC",  # North Carolina
    "TN",  # Tennessee
    "VA",  # Virginia
    "KY",  # Kentucky (newer market)
]


def collect_data_for_state(db, state: str) -> dict:
    """Collect all data for a single state"""
    collector = DataCollectorAgent(db)

    results = {
        "state": state,
        "publix_stores": 0,
        "competitor_stores": 0,
        "demographics": 0,
        "zoning_records": 0,
        "errors": [],
    }

    print(f"\n{'='*60}")
    print(f"Collecting data for {state}")
    print(f"{'='*60}\n")

    # 1. Collect Publix stores
    print(f"1. Collecting Publix stores in {state}...")
    try:
        stores = collector.collect_publix_stores(state=state)
        results["publix_stores"] = len(stores)
        print(f"   ✅ Collected {len(stores)} Publix stores")
    except Exception as e:
        error_msg = f"Publix stores: {str(e)}"
        results["errors"].append(error_msg)
        print(f"   ⚠️  Error: {e}")

    # 2. Collect competitor stores
    print(f"\n2. Collecting competitor stores in {state}...")
    try:
        competitors = collector.collect_competitor_stores(state=state)
        total_competitors = sum(len(stores) for stores in competitors.values())
        results["competitor_stores"] = total_competitors
        print(f"   ✅ Collected {total_competitors} competitor stores")
        for name, stores in competitors.items():
            print(f"      - {name}: {len(stores)} stores")
    except Exception as e:
        error_msg = f"Competitor stores: {str(e)}"
        results["errors"].append(error_msg)
        print(f"   ⚠️  Error: {e}")

    # 3. Collect demographics for major cities
    print(f"\n3. Collecting demographics...")
    # Get cities from collected stores
    try:
        from app.models.schemas import PublixStore

        stores_in_db = db.query(PublixStore).filter(PublixStore.state == state).all()
        cities = list(set([(s.city, state) for s in stores_in_db]))[
            :20
        ]  # Top 20 cities

        if not cities:
            # Use default major cities for the state
            cities = get_major_cities(state)

        city_dicts = [{"city": city, "state": st} for city, st in cities]
        demographics = collector.collect_demographics(city_dicts)
        results["demographics"] = len(demographics)
        print(f"   ✅ Collected demographics for {len(demographics)} cities")
    except Exception as e:
        error_msg = f"Demographics: {str(e)}"
        results["errors"].append(error_msg)
        print(f"   ⚠️  Error: {e}")

    # 4. Collect zoning records
    print(f"\n4. Collecting zoning records...")
    try:
        if cities:
            city_dicts = [{"city": city, "state": st} for city, st in cities]
            zoning = collector.collect_zoning_records(
                city_dicts, min_acreage=15.0, max_acreage=25.0
            )
            results["zoning_records"] = len(zoning)
            print(f"   ✅ Collected {len(zoning)} zoning records")
    except Exception as e:
        error_msg = f"Zoning records: {str(e)}"
        results["errors"].append(error_msg)
        print(f"   ⚠️  Error: {e}")

    return results


def get_major_cities(state: str) -> List[tuple]:
    """Get major cities for a state"""
    major_cities = {
        "FL": [
            ("Miami", "FL"),
            ("Tampa", "FL"),
            ("Orlando", "FL"),
            ("Jacksonville", "FL"),
            ("Tallahassee", "FL"),
            ("Fort Lauderdale", "FL"),
            ("Pensacola", "FL"),
            ("Sarasota", "FL"),
        ],
        "GA": [
            ("Atlanta", "GA"),
            ("Savannah", "GA"),
            ("Augusta", "GA"),
            ("Columbus", "GA"),
            ("Macon", "GA"),
        ],
        "AL": [
            ("Birmingham", "AL"),
            ("Montgomery", "AL"),
            ("Mobile", "AL"),
            ("Huntsville", "AL"),
        ],
        "SC": [
            ("Charleston", "SC"),
            ("Columbia", "SC"),
            ("Greenville", "SC"),
            ("Myrtle Beach", "SC"),
        ],
        "NC": [
            ("Charlotte", "NC"),
            ("Raleigh", "NC"),
            ("Greensboro", "NC"),
            ("Asheville", "NC"),
        ],
        "TN": [
            ("Nashville", "TN"),
            ("Memphis", "TN"),
            ("Knoxville", "TN"),
            ("Chattanooga", "TN"),
        ],
        "VA": [
            ("Richmond", "VA"),
            ("Virginia Beach", "VA"),
            ("Norfolk", "VA"),
            ("Charlottesville", "VA"),
        ],
        "KY": [
            ("Lexington", "KY"),
            ("Louisville", "KY"),
            ("Bowling Green", "KY"),
            ("Owensboro", "KY"),
        ],
    }
    return major_cities.get(state, [])


def collect_all_data(states: List[str] = None):
    """Collect data for multiple states"""
    if states is None:
        states = PUBLIX_STATES

    db = SessionLocal()

    try:
        all_results = []

        print("=" * 60)
        print("PUBLIX EXPANSION PREDICTOR - DATA COLLECTION")
        print("=" * 60)
        print(f"\nCollecting data for {len(states)} states: {', '.join(states)}")
        print("\nThis may take a while...")

        for state in states:
            try:
                result = collect_data_for_state(db, state)
                all_results.append(result)
            except Exception as e:
                logger.error(f"Failed to collect data for {state}: {e}", exc_info=True)
                all_results.append(
                    {
                        "state": state,
                        "publix_stores": 0,
                        "competitor_stores": 0,
                        "demographics": 0,
                        "zoning_records": 0,
                        "errors": [f"Collection failed: {str(e)}"],
                    }
                )

        # Summary
        print("\n" + "=" * 60)
        print("COLLECTION SUMMARY")
        print("=" * 60)

        total_stores = sum(r["publix_stores"] for r in all_results)
        total_competitors = sum(r["competitor_stores"] for r in all_results)
        total_demos = sum(r["demographics"] for r in all_results)
        total_zoning = sum(r["zoning_records"] for r in all_results)

        print(f"\nTotal Publix Stores: {total_stores}")
        print(f"Total Competitor Stores: {total_competitors}")
        print(f"Total Demographics Records: {total_demos}")
        print(f"Total Zoning Records: {total_zoning}")

        print("\nBy State:")
        for result in all_results:
            print(f"\n{result['state']}:")
            print(f"  Publix Stores: {result['publix_stores']}")
            print(f"  Competitor Stores: {result['competitor_stores']}")
            print(f"  Demographics: {result['demographics']}")
            print(f"  Zoning Records: {result['zoning_records']}")
            if result["errors"]:
                print(f"  Errors: {len(result['errors'])}")
                for error in result["errors"]:
                    print(f"    - {error}")

        print("\n✅ Data collection complete!")
        print("\nNext steps:")
        print("  1. Verify data: curl http://localhost:8000/api/dashboard/stats")
        print(
            "  2. Run analysis: curl -X POST http://localhost:8000/api/analyze -H 'Content-Type: application/json' -d '{\"region\": \"FL\"}'"
        )
        print("  3. View stores: curl http://localhost:8000/api/stores?state=FL")

    finally:
        db.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Collect comprehensive data for Publix expansion analysis"
    )
    parser.add_argument(
        "--states",
        nargs="+",
        help="State codes to collect (e.g., FL GA AL). Default: all Publix states",
    )
    parser.add_argument(
        "--state",
        help="Single state code (shorthand for --states STATE)",
    )

    args = parser.parse_args()

    states_to_collect = args.states or ([args.state] if args.state else None)

    collect_all_data(states_to_collect)
