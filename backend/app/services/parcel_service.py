"""
Parcel service for collecting 15-25 acre commercial parcels from county GIS systems

Note: County GIS systems vary widely. This service provides a framework that can be
extended for specific county APIs.
"""

import os
import requests
import logging
from typing import List, Dict, Optional
from datetime import datetime
import time

logger = logging.getLogger(__name__)


class ParcelService:
    """Service for collecting parcel data using Smarty API and county GIS systems"""

    def __init__(self, db=None):
        self.db = db
        self.rate_limiter_delay = 1.0  # 1 second between requests

        # Initialize Smarty service if available
        try:
            from app.services.smarty_service import SmartyService

            self.smarty_service = SmartyService()
            if self.smarty_service.available:
                logger.info("Smarty API available for parcel data")
            else:
                logger.warning("Smarty API credentials not configured")
                self.smarty_service = None
        except Exception as e:
            logger.warning(f"Failed to initialize Smarty service: {e}")
            self.smarty_service = None

    def get_parcels_by_city(
        self,
        city: str,
        state: str,
        min_acreage: float = 15.0,
        max_acreage: float = 25.0,
    ) -> List[Dict]:
        """
        Get parcels in a city within acreage range using Smarty API

        Args:
            city: City name
            state: State abbreviation
            min_acreage: Minimum parcel size in acres
            max_acreage: Maximum parcel size in acres

        Returns:
            List of parcel dictionaries
        """
        logger.info(
            f"Getting parcels for {city}, {state} ({min_acreage}-{max_acreage} acres)"
        )

        parcels = []

        # Use Smarty API if available
        if self.smarty_service and self.smarty_service.available:
            try:
                # Get addresses from stores/competitors in the city as starting points
                # Then use Smarty to get property data for those addresses
                if self.db:
                    from app.models.schemas import PublixStore, CompetitorStore

                    # Get addresses from stores in this city
                    store_addresses = (
                        self.db.query(PublixStore)
                        .filter(PublixStore.city == city, PublixStore.state == state)
                        .limit(50)
                        .all()
                    )

                    competitor_addresses = (
                        self.db.query(CompetitorStore)
                        .filter(
                            CompetitorStore.city == city, CompetitorStore.state == state
                        )
                        .limit(50)
                        .all()
                    )

                    # Process addresses through Smarty
                    addresses_to_check = []
                    for store in store_addresses:
                        if store.address:
                            addresses_to_check.append(
                                {
                                    "address": store.address,
                                    "city": city,
                                    "state": state,
                                    "zip_code": store.zip_code,
                                }
                            )

                    for comp in competitor_addresses:
                        if comp.address:
                            addresses_to_check.append(
                                {
                                    "address": comp.address,
                                    "city": city,
                                    "state": state,
                                    "zip_code": comp.zip_code,
                                }
                            )

                    # Get property data from Smarty
                    properties = self.smarty_service.batch_get_properties(
                        addresses_to_check
                    )

                    # Filter by acreage and convert to parcel format
                    for prop in properties:
                        # Extract acreage from property data (structure depends on Smarty API)
                        property_data = prop.get("property_data", {})
                        acreage = property_data.get("acreage") or property_data.get(
                            "lot_size_acres"
                        )

                        if acreage and min_acreage <= acreage <= max_acreage:
                            parcel = {
                                "parcel_id": property_data.get("apn")
                                or property_data.get("parcel_id"),
                                "address": prop.get("address"),
                                "city": city,
                                "state": state,
                                "acreage": acreage,
                                "current_zoning": property_data.get("zoning")
                                or property_data.get("zoning_code"),
                                "assessed_value": property_data.get("assessed_value")
                                or property_data.get("tax_assessed_value"),
                                "land_use_code": property_data.get("land_use_code"),
                                "latitude": prop.get("latitude"),
                                "longitude": prop.get("longitude"),
                                "owner_name": property_data.get("owner_name"),
                                "owner_type": property_data.get("owner_type"),
                                "additional_data": property_data,
                            }
                            parcels.append(parcel)

                    logger.info(f"Found {len(parcels)} parcels via Smarty API")
            except Exception as e:
                logger.error(f"Error getting parcels via Smarty: {e}", exc_info=True)
        else:
            logger.warning("Smarty API not available - cannot get parcel data")

        return parcels

    def get_parcels_near_anchors(
        self,
        latitude: float,
        longitude: float,
        radius_miles: float = 2.0,
        min_acreage: float = 15.0,
        max_acreage: float = 25.0,
    ) -> List[Dict]:
        """
        Get parcels within radius of a point (e.g., near anchor store)

        Args:
            latitude: Center point latitude
            longitude: Center point longitude
            radius_miles: Search radius in miles
            min_acreage: Minimum parcel size
            max_acreage: Maximum parcel size

        Returns:
            List of parcel dictionaries
        """
        logger.info(
            f"Getting parcels near ({latitude}, {longitude}) "
            f"within {radius_miles} miles, {min_acreage}-{max_acreage} acres"
        )
        # Implementation depends on GIS system spatial query capabilities
        return []

    def _haversine_distance(
        self, lat1: float, lon1: float, lat2: float, lon2: float
    ) -> float:
        """Calculate distance between two points in miles"""
        import math

        R = 3959  # Earth radius in miles
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)

        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(math.radians(lat1))
            * math.cos(math.radians(lat2))
            * math.sin(dlon / 2) ** 2
        )
        c = 2 * math.asin(math.sqrt(a))

        return R * c


# County-specific implementations would extend this base class
# Example for Kentucky counties:


class KentuckyParcelService(ParcelService):
    """Kentucky-specific parcel service"""

    def __init__(self):
        super().__init__()
        # Kentucky has a unified property valuation administrator (PVA) system
        # Each county has its own PVA website, but many use similar structures
        self.base_urls = {
            "Daviess": "https://daviesspva.com",  # Owensboro
            "Fayette": "https://fayettepva.com",  # Lexington
            "Jefferson": "https://jeffersonpva.com",  # Louisville
        }

    def get_parcels_by_city(
        self,
        city: str,
        state: str,
        min_acreage: float = 15.0,
        max_acreage: float = 25.0,
    ) -> List[Dict]:
        """Get parcels for Kentucky cities"""
        if state != "KY":
            return []

        # Map city to county
        city_to_county = {
            "Owensboro": "Daviess",
            "Lexington": "Fayette",
            "Louisville": "Jefferson",
            "Bowling Green": "Warren",
        }

        county = city_to_county.get(city)
        if not county:
            logger.warning(f"No county mapping for {city}, KY")
            return []

        # Note: Actual implementation would need to:
        # 1. Access county PVA API or scrape website
        # 2. Filter by acreage
        # 3. Extract parcel data
        # This is a placeholder structure

        logger.info(f"Would query {county} County PVA for {city}")
        return []


# Similar implementations would be created for other states:
# - FloridaParcelService (varies by county)
# - GeorgiaParcelService
# etc.
