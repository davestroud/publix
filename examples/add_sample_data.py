"""
Script to add sample data to the database for testing

This adds sample Publix stores, competitor stores, demographics, and zoning records
so you can test the API endpoints.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.services.database import SessionLocal
from app.models.schemas import PublixStore, CompetitorStore, Demographics, ZoningRecord
from datetime import datetime


def add_sample_data():
    """Add sample data to the database"""
    db = SessionLocal()

    try:
        # Sample Publix Stores (Kentucky)
        publix_stores = [
            PublixStore(
                store_number="KY001",
                address="123 Main Street",
                city="Lexington",
                state="KY",
                zip_code="40502",
                latitude=38.0406,
                longitude=-84.5037,
                square_feet=45000,
                opening_date=datetime(2020, 3, 15),
            ),
            PublixStore(
                store_number="KY002",
                address="456 Broadway",
                city="Louisville",
                state="KY",
                zip_code="40202",
                latitude=38.2527,
                longitude=-85.7585,
                square_feet=50000,
                opening_date=datetime(2021, 6, 20),
            ),
            PublixStore(
                store_number="KY003",
                address="789 Winchester Road",
                city="Lexington",
                state="KY",
                zip_code="40505",
                latitude=38.0500,
                longitude=-84.4500,
                square_feet=48000,
                opening_date=datetime(2022, 9, 10),
            ),
        ]

        # Sample Competitor Stores
        competitor_stores = [
            CompetitorStore(
                competitor_name="Walmart",
                address="1000 Commerce Drive",
                city="Bowling Green",
                state="KY",
                zip_code="42101",
                latitude=36.9685,
                longitude=-86.4808,
                square_feet=150000,
            ),
            CompetitorStore(
                competitor_name="Kroger",
                address="200 Market Street",
                city="Bowling Green",
                state="KY",
                zip_code="42101",
                latitude=36.9700,
                longitude=-86.4700,
                square_feet=60000,
            ),
            CompetitorStore(
                competitor_name="Walmart",
                address="300 Retail Blvd",
                city="Owensboro",
                state="KY",
                zip_code="42301",
                latitude=37.7719,
                longitude=-87.1111,
                square_feet=140000,
            ),
        ]

        # Sample Demographics
        demographics = [
            Demographics(
                city="Bowling Green",
                state="KY",
                population=72000,
                median_income=45000.0,
                growth_rate=0.025,
                median_age=32.5,
                household_size=2.4,
                data_year=2023,
            ),
            Demographics(
                city="Owensboro",
                state="KY",
                population=60000,
                median_income=42000.0,
                growth_rate=0.018,
                median_age=35.0,
                household_size=2.3,
                data_year=2023,
            ),
            Demographics(
                city="Paducah",
                state="KY",
                population=25000,
                median_income=38000.0,
                growth_rate=0.012,
                median_age=38.0,
                household_size=2.2,
                data_year=2023,
            ),
        ]

        # Sample Zoning Records
        zoning_records = [
            ZoningRecord(
                parcel_id="KY-BG-2024-001",
                address="1234 Scottsville Road",
                city="Bowling Green",
                state="KY",
                latitude=36.9685,
                longitude=-86.4808,
                acreage=18.5,
                zoning_status="pending",
                permit_type="commercial",
                description="Commercial rezoning request for retail development",
                record_date=datetime(2024, 1, 10),
            ),
            ZoningRecord(
                parcel_id="KY-BG-2024-002",
                address="5678 Nashville Road",
                city="Bowling Green",
                state="KY",
                latitude=36.9700,
                longitude=-86.4700,
                acreage=22.0,
                zoning_status="approved",
                permit_type="commercial",
                description="Approved commercial development site",
                record_date=datetime(2024, 2, 15),
            ),
            ZoningRecord(
                parcel_id="KY-OW-2024-001",
                address="9012 Frederica Street",
                city="Owensboro",
                state="KY",
                latitude=37.7719,
                longitude=-87.1111,
                acreage=16.8,
                zoning_status="pending",
                permit_type="rezoning",
                description="Rezoning from agricultural to commercial",
                record_date=datetime(2024, 3, 1),
            ),
        ]

        # Add all data
        print("Adding sample data to database...")

        for store in publix_stores:
            db.add(store)
        print(f"  ✓ Added {len(publix_stores)} Publix stores")

        for competitor in competitor_stores:
            db.add(competitor)
        print(f"  ✓ Added {len(competitor_stores)} competitor stores")

        for demo in demographics:
            db.add(demo)
        print(f"  ✓ Added {len(demographics)} demographic records")

        for zoning in zoning_records:
            db.add(zoning)
        print(f"  ✓ Added {len(zoning_records)} zoning records")

        db.commit()
        print("\n✅ Sample data added successfully!")
        print("\nYou can now:")
        print("  - Query stores: curl http://localhost:8000/api/stores")
        print(
            "  - Query demographics: curl 'http://localhost:8000/api/demographics/Bowling%20Green?state=KY'"
        )
        print("  - Query zoning: curl 'http://localhost:8000/api/zoning/KY'")
        print(
            "  - Run analysis: curl -X POST http://localhost:8000/api/analyze -H 'Content-Type: application/json' -d '{\"region\": \"KY\"}'"
        )

    except Exception as e:
        db.rollback()
        print(f"❌ Error adding data: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    add_sample_data()
