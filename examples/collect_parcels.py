"""
Script to collect parcel data using Smarty API

Collects parcels (15-25 acres) for cities where Publix operates.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.services.database import SessionLocal
from app.agents.data_collector import DataCollectorAgent
from app.models.schemas import PublixStore, Parcel
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def collect_parcels_for_cities():
    """Collect parcels for cities with Publix stores"""
    db = SessionLocal()

    try:
        collector = DataCollectorAgent(db)

        # Get cities that have Publix stores
        cities_with_stores = (
            db.query(PublixStore.city, PublixStore.state)
            .distinct()
            .limit(20)  # Start with 20 cities
            .all()
        )

        print(f"\n{'='*60}")
        print(f"Collecting parcels for {len(cities_with_stores)} cities")
        print(f"{'='*60}\n")

        total_parcels = 0
        for city, state in cities_with_stores:
            print(f"\n📍 Collecting parcels for {city}, {state}...")

            try:
                parcels = collector.collect_parcels(
                    city=city,
                    state=state,
                    min_acreage=15.0,
                    max_acreage=25.0,
                )

                if parcels:
                    print(f"   ✅ Found {len(parcels)} parcels")
                    total_parcels += len(parcels)

                    # Show sample parcel
                    if parcels:
                        sample = parcels[0]
                        print(
                            f"   Sample: {sample.get('address', 'N/A')} - {sample.get('acreage', 'N/A')} acres"
                        )
                else:
                    print(
                        f"   ⚠️  No parcels found (may need more addresses or Smarty API may not have property data)"
                    )

            except Exception as e:
                logger.error(
                    f"Error collecting parcels for {city}, {state}: {e}", exc_info=True
                )
                print(f"   ❌ Error: {e}")

        print(f"\n{'='*60}")
        print(f"✅ Collection complete!")
        print(f"   Total parcels collected: {total_parcels}")
        print(f"{'='*60}\n")

        # Show summary
        total_in_db = db.query(Parcel).count()
        print(f"Total parcels in database: {total_in_db}")

    except Exception as e:
        logger.error(f"Collection failed: {e}", exc_info=True)
        print(f"\n❌ Collection failed: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    collect_parcels_for_cities()
