"""
Add sample parcels for testing map display

Creates a few sample parcels with coordinates so we can test the map view.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.services.database import SessionLocal
from app.models.schemas import Parcel
from datetime import datetime


def add_sample_parcels():
    """Add sample parcels for testing"""
    db = SessionLocal()

    try:
        # Sample parcels in Florida (where Publix has many stores)
        sample_parcels = [
            {
                "parcel_id": "SAMPLE-001",
                "address": "123 Main Street",
                "city": "Orlando",
                "state": "FL",
                "acreage": 18.5,
                "current_zoning": "C-2",
                "assessed_value": 2500000.0,
                "land_use_code": "Commercial",
                "latitude": 28.5383,
                "longitude": -81.3792,
                "owner_name": "Sample Owner LLC",
                "owner_type": "LLC",
            },
            {
                "parcel_id": "SAMPLE-002",
                "address": "456 Commerce Blvd",
                "city": "Tampa",
                "state": "FL",
                "acreage": 22.0,
                "current_zoning": "C-3",
                "assessed_value": 3200000.0,
                "land_use_code": "Commercial",
                "latitude": 27.9506,
                "longitude": -82.4572,
                "owner_name": "Development Corp",
                "owner_type": "Corporation",
            },
            {
                "parcel_id": "SAMPLE-003",
                "address": "789 Retail Way",
                "city": "Jacksonville",
                "state": "FL",
                "acreage": 16.8,
                "current_zoning": "C-2",
                "assessed_value": 1800000.0,
                "land_use_code": "Commercial",
                "latitude": 30.3322,
                "longitude": -81.6557,
                "owner_name": "Property Holdings Inc",
                "owner_type": "Corporation",
            },
            {
                "parcel_id": "SAMPLE-004",
                "address": "321 Business Park Dr",
                "city": "Miami",
                "state": "FL",
                "acreage": 20.3,
                "current_zoning": "C-3",
                "assessed_value": 4500000.0,
                "land_use_code": "Commercial",
                "latitude": 25.7617,
                "longitude": -80.1918,
                "owner_name": "Miami Realty Group",
                "owner_type": "LLC",
            },
            {
                "parcel_id": "SAMPLE-005",
                "address": "654 Market Square",
                "city": "Atlanta",
                "state": "GA",
                "acreage": 19.2,
                "current_zoning": "C-2",
                "assessed_value": 2800000.0,
                "land_use_code": "Commercial",
                "latitude": 33.7490,
                "longitude": -84.3880,
                "owner_name": "Atlanta Properties",
                "owner_type": "LLC",
            },
        ]

        added_count = 0
        for parcel_data in sample_parcels:
            # Check if parcel already exists
            existing = (
                db.query(Parcel).filter_by(parcel_id=parcel_data["parcel_id"]).first()
            )
            if existing:
                print(
                    f"⚠️  Parcel {parcel_data['parcel_id']} already exists, skipping..."
                )
                continue

            parcel = Parcel(**parcel_data)
            db.add(parcel)
            added_count += 1

        db.commit()
        print(f"\n✅ Added {added_count} sample parcels")
        print(f"   Total parcels in database: {db.query(Parcel).count()}")

        print("\n📍 Sample parcels added:")
        for p in sample_parcels[:added_count]:
            print(
                f"   - {p['address']}, {p['city']}, {p['state']} ({p['acreage']} acres)"
            )

    except Exception as e:
        db.rollback()
        print(f"\n❌ Error adding sample parcels: {e}")
        import traceback

        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    add_sample_parcels()
