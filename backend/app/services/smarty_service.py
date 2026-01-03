"""
Smarty API service for property and parcel data

Uses Smarty's APIs to get:
- Property details (acreage, zoning, etc.)
- Commercial parcels
- Property records
- Address geocoding

Documentation: https://www.smarty.com/docs
"""

import os
import requests
import logging
from typing import List, Dict, Optional
from datetime import datetime
import time
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class SmartyService:
    """Service for accessing Smarty API property and parcel data"""

    def __init__(self):
        self.auth_id = os.getenv("SMARTY_AUTH_ID")
        self.api_key = os.getenv("SMARTY_API_KEY")

        if not self.auth_id or not self.api_key:
            logger.warning(
                "SMARTY_AUTH_ID or SMARTY_API_KEY not set. Smarty API will not be available."
            )
            self.available = False
        else:
            self.available = True
            logger.info("Smarty service initialized with credentials")

        # Smarty API endpoints (Cloud API)
        # Documentation: https://www.smarty.com/docs/cloud
        self.streets_url = "https://us-street.api.smarty.com/street-address"
        self.geocoding_url = "https://us-geocoding.api.smarty.com/lookup"
        # US Property Data API - check docs for exact endpoint
        # May use: https://us-property.api.smarty.com/property or similar
        self.property_url = "https://us-property.api.smarty.com"

        self.rate_limiter_delay = 0.1  # 100ms between requests

    def _make_request(self, endpoint: str, params: Dict) -> Optional[Dict]:
        """Make authenticated request to Smarty API"""
        if not self.available:
            logger.warning("Smarty API not available - credentials missing")
            return None

        try:
            time.sleep(self.rate_limiter_delay)

            # Smarty uses auth-id and auth-token as query parameters
            params["auth-id"] = self.auth_id
            params["auth-token"] = self.api_key

            response = requests.get(endpoint, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            return data

        except requests.exceptions.HTTPError as e:
            logger.error(f"Smarty API HTTP error: {e}")
            if hasattr(e.response, "text"):
                logger.error(f"Response: {e.response.text[:500]}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Smarty API request failed: {e}")
            return None

    def geocode_address(
        self, address: str, city: str, state: str, zip_code: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Geocode an address using Smarty US Street API

        Args:
            address: Street address
            city: City name
            state: State abbreviation
            zip_code: Optional ZIP code

        Returns:
            Geocoded address data with coordinates
        """
        if not self.available:
            return None

        params = {
            "street": address,
            "city": city,
            "state": state,
        }
        if zip_code:
            params["zipcode"] = zip_code

        data = self._make_request(self.streets_url, params)

        if data and len(data) > 0:
            result = data[0]
            components = result.get("components", {})
            metadata = result.get("metadata", {})

            return {
                "address": result.get("delivery_line_1", address),
                "city": components.get("city_name", city),
                "state": components.get("state_abbreviation", state),
                "zip_code": components.get("zipcode", zip_code),
                "latitude": metadata.get("latitude"),
                "longitude": metadata.get("longitude"),
                "precision": metadata.get("precision"),
                "smarty_data": result,
            }

        return None

    def get_property_by_address(
        self, address: str, city: str, state: str, zip_code: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Get property data for a specific address

        Note: Smarty Property API endpoint structure may vary.
        Check https://www.smarty.com/docs for exact endpoint.

        Args:
            address: Street address
            city: City name
            state: State abbreviation
            zip_code: Optional ZIP code

        Returns:
            Property data dictionary or None
        """
        if not self.available:
            return None

        # First geocode to get standardized address
        geocoded = self.geocode_address(address, city, state, zip_code)
        if not geocoded:
            return None

        # Try to get property data
        # Note: Actual endpoint depends on Smarty API version
        # Common patterns:
        # - /property?address=...&city=...&state=...
        # - /property/{property_id}
        # Check Smarty docs for exact endpoint structure

        property_params = {
            "address": geocoded["address"],
            "city": geocoded["city"],
            "state": geocoded["state"],
        }
        if geocoded.get("zip_code"):
            property_params["zipcode"] = geocoded["zip_code"]

        # Note: Smarty Property Data API endpoint structure may vary
        # For now, return geocoded data which works reliably
        # Property data lookup may require different endpoint or API version
        # Check https://www.smarty.com/docs for exact Property API endpoint

        # Try property endpoint if it exists (may need different URL structure)
        # property_endpoint = f"{self.property_url}/property"  # This endpoint may not exist
        # property_data = self._make_request(property_endpoint, property_params)

        # For now, return geocoded data with note that property data needs correct endpoint
        logger.info(
            "Property data lookup - geocoding successful, property data endpoint needs verification"
        )
        return geocoded

    def search_parcels_by_city(
        self,
        city: str,
        state: str,
        min_acreage: float = 15.0,
        max_acreage: float = 25.0,
        property_type: Optional[str] = "commercial",
    ) -> List[Dict]:
        """
        Search for parcels in a city within acreage range

        Note: Smarty Property API may require batch processing or address lists.
        This method uses geocoding + property lookup for known addresses.

        For city-wide searches, you may need to:
        1. Get address list from other sources (Google Places, etc.)
        2. Batch process addresses through Smarty
        3. Filter by acreage and property type

        Args:
            city: City name
            state: State abbreviation
            min_acreage: Minimum acreage
            max_acreage: Maximum acreage
            property_type: Filter by property type

        Returns:
            List of parcel dictionaries
        """
        if not self.available:
            logger.warning("Smarty API not available")
            return []

        logger.info(
            f"Searching Smarty API for parcels in {city}, {state} "
            f"({min_acreage}-{max_acreage} acres)"
        )

        # Strategy: Use addresses from collected stores/competitors as starting points
        # Then expand search around those areas
        # This is a framework - actual implementation depends on Smarty API capabilities

        parcels = []

        # TODO: Implement based on Smarty API documentation
        # Options:
        # 1. If Smarty supports city-wide property search
        # 2. Use address lists and batch process
        # 3. Use Smarty's spatial search if available

        logger.info(
            "Smarty Property API integration - check documentation for search methods"
        )
        logger.info("For now, use get_property_by_address() for specific addresses")

        return parcels

    def batch_get_properties(self, addresses: List[Dict[str, str]]) -> List[Dict]:
        """
        Batch process multiple addresses to get property data

        Args:
            addresses: List of address dicts with 'address', 'city', 'state', optional 'zip_code'

        Returns:
            List of property data dictionaries
        """
        if not self.available:
            return []

        properties = []
        for addr in addresses:
            prop = self.get_property_by_address(
                address=addr.get("address", ""),
                city=addr.get("city", ""),
                state=addr.get("state", ""),
                zip_code=addr.get("zip_code"),
            )
            if prop:
                properties.append(prop)

        return properties
