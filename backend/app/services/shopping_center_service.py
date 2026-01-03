"""
Shopping Center Service - Collects shopping center and co-tenancy data
Uses Google Places API to identify shopping centers and anchor tenants
"""

import os
import requests
import logging
from typing import List, Dict, Optional
import time
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class ShoppingCenterService:
    """Service for collecting shopping center data using Google Places API"""

    def __init__(self):
        self.api_key = os.getenv("GOOGLE_PLACES_API_KEY")
        if not self.api_key:
            logger.warning(
                "GOOGLE_PLACES_API_KEY not set. Shopping center service unavailable."
            )
            self.available = False
        else:
            self.available = True
            self.base_url = "https://places.googleapis.com/v1/places:searchText"
            logger.info("Shopping center service initialized")

    def find_shopping_centers(
        self, city: str, state: str, radius_miles: float = 10.0
    ) -> List[Dict]:
        """
        Find shopping centers and malls in a city

        Args:
            city: City name
            state: State abbreviation
            radius_miles: Search radius in miles

        Returns:
            List of shopping center dictionaries
        """
        if not self.available:
            return []

        shopping_centers = []
        query = f"shopping center mall in {city}, {state}"

        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress,places.location,places.types,places.rating,places.userRatingCount",
        }

        payload = {
            "textQuery": query,
            "maxResultCount": 20,
            "includedType": "shopping_mall",
        }

        try:
            response = requests.post(
                self.base_url, json=payload, headers=headers, timeout=10
            )
            response.raise_for_status()
            data = response.json()
            places = data.get("places", [])

            for place in places:
                center = {
                    "name": place.get("displayName", {}).get("text", ""),
                    "address": place.get("formattedAddress", ""),
                    "latitude": place.get("location", {}).get("latitude"),
                    "longitude": place.get("location", {}).get("longitude"),
                    "rating": place.get("rating"),
                    "user_rating_count": place.get("userRatingCount"),
                    "place_id": place.get("id"),
                    "types": place.get("types", []),
                    "city": city,
                    "state": state,
                }
                shopping_centers.append(center)

            logger.info(
                f"Found {len(shopping_centers)} shopping centers in {city}, {state}"
            )

        except Exception as e:
            logger.error(f"Error finding shopping centers: {e}", exc_info=True)

        return shopping_centers

    def find_anchor_tenants(
        self, latitude: float, longitude: float, radius_meters: int = 2000
    ) -> List[Dict]:
        """
        Find anchor tenants (Target, Walmart, etc.) near a location

        Args:
            latitude: Center point latitude
            longitude: Center point longitude
            radius_meters: Search radius in meters (default 2km)

        Returns:
            List of anchor tenant dictionaries
        """
        if not self.available:
            return []

        anchor_tenants = []
        anchor_brands = [
            "Target",
            "Walmart",
            "Costco",
            "Kroger",
            "Home Depot",
            "Lowe's",
            "Best Buy",
            "Macy's",
            "JCPenney",
            "Sears",
        ]

        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress,places.location,places.types",
        }

        for brand in anchor_brands:
            try:
                # Use nearby search for each anchor brand
                nearby_url = "https://places.googleapis.com/v1/places:searchNearby"
                payload = {
                    "includedTypes": ["department_store", "supermarket", "store"],
                    "maxResultCount": 5,
                    "locationRestriction": {
                        "circle": {
                            "center": {"latitude": latitude, "longitude": longitude},
                            "radius": radius_meters,
                        }
                    },
                }

                response = requests.post(
                    nearby_url, json=payload, headers=headers, timeout=10
                )
                response.raise_for_status()
                data = response.json()
                places = data.get("places", [])

                for place in places:
                    name = place.get("displayName", {}).get("text", "")
                    if brand.lower() in name.lower():
                        anchor = {
                            "brand": brand,
                            "name": name,
                            "address": place.get("formattedAddress", ""),
                            "latitude": place.get("location", {}).get("latitude"),
                            "longitude": place.get("location", {}).get("longitude"),
                            "place_id": place.get("id"),
                            "types": place.get("types", []),
                        }
                        anchor_tenants.append(anchor)

                time.sleep(0.1)  # Rate limiting

            except Exception as e:
                logger.debug(f"Error finding {brand}: {e}")
                continue

        logger.info(f"Found {len(anchor_tenants)} anchor tenants")
        return anchor_tenants

    def analyze_co_tenancy(
        self, city: str, state: str, latitude: float, longitude: float
    ) -> Dict:
        """
        Analyze co-tenancy quality for a potential Publix location

        Args:
            city: City name
            state: State abbreviation
            latitude: Potential location latitude
            longitude: Potential location longitude

        Returns:
            Dictionary with co-tenancy analysis
        """
        if not self.available:
            return {}

        # Find nearby shopping centers
        shopping_centers = self.find_shopping_centers(city, state)

        # Find anchor tenants within 2km
        anchors = self.find_anchor_tenants(latitude, longitude, radius_meters=2000)

        # Calculate distances and scores
        co_tenancy_score = 0
        nearby_centers = []
        nearby_anchors = []

        # Score based on anchor tenants
        anchor_brands_found = set()
        for anchor in anchors:
            brand = anchor.get("brand", "")
            if brand:
                anchor_brands_found.add(brand)
                nearby_anchors.append(anchor)

        # High-value anchors (Target, Walmart, Costco)
        high_value_anchors = {"Target", "Walmart", "Costco"}
        high_value_count = len(anchor_brands_found & high_value_anchors)

        # Calculate score (0-100)
        co_tenancy_score = min(
            100, (len(anchor_brands_found) * 10) + (high_value_count * 20)
        )

        return {
            "co_tenancy_score": co_tenancy_score,
            "nearby_shopping_centers": len(shopping_centers),
            "nearby_anchor_tenants": len(nearby_anchors),
            "anchor_brands": list(anchor_brands_found),
            "high_value_anchors": high_value_count,
            "shopping_centers": shopping_centers[:5],  # Top 5
            "anchor_tenants": nearby_anchors,
            "recommendation": (
                "Excellent"
                if co_tenancy_score >= 70
                else (
                    "Good"
                    if co_tenancy_score >= 50
                    else "Fair" if co_tenancy_score >= 30 else "Poor"
                )
            ),
        }
