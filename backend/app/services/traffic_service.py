"""
Traffic Analysis Service - Collects traffic volume and accessibility data
Uses Google Maps Distance Matrix API and other sources
"""

import os
import requests
import logging
from typing import List, Dict, Optional
import time
from dotenv import load_dotenv
import math

load_dotenv()
logger = logging.getLogger(__name__)


class TrafficService:
    """Service for collecting traffic and accessibility data"""

    def __init__(self):
        self.google_api_key = os.getenv("GOOGLE_PLACES_API_KEY")
        if not self.google_api_key:
            logger.warning("GOOGLE_PLACES_API_KEY not set. Traffic service limited.")
            self.available = False
        else:
            self.available = True
            self.distance_matrix_url = (
                "https://maps.googleapis.com/maps/api/distancematrix/json"
            )
            logger.info("Traffic service initialized")

    def calculate_accessibility_score(
        self, latitude: float, longitude: float, city: str, state: str
    ) -> Dict:
        """
        Calculate accessibility score for a location
        Uses travel times to nearby residential areas and major roads

        Args:
            latitude: Location latitude
            longitude: Location longitude
            city: City name
            state: State abbreviation

        Returns:
            Dictionary with accessibility metrics
        """
        if not self.available:
            return {"accessibility_score": 0.5, "error": "API not available"}

        # Sample residential areas (in production, get from demographics data)
        residential_points = [
            {"lat": latitude + 0.05, "lng": longitude},  # North
            {"lat": latitude - 0.05, "lng": longitude},  # South
            {"lat": latitude, "lng": longitude + 0.05},  # East
            {"lat": latitude, "lng": longitude - 0.05},  # West
        ]

        origins = f"{latitude},{longitude}"
        destinations = "|".join([f"{p['lat']},{p['lng']}" for p in residential_points])

        try:
            params = {
                "origins": origins,
                "destinations": destinations,
                "key": self.google_api_key,
                "mode": "driving",
                "units": "imperial",
            }

            response = requests.get(self.distance_matrix_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get("status") != "OK":
                logger.warning(f"Distance Matrix API error: {data.get('status')}")
                return {"accessibility_score": 0.5}

            total_time = 0
            valid_routes = 0

            for row in data.get("rows", []):
                for element in row.get("elements", []):
                    if element.get("status") == "OK":
                        duration = element.get("duration", {}).get(
                            "value", 0
                        )  # seconds
                        total_time += duration
                        valid_routes += 1

            if valid_routes == 0:
                return {"accessibility_score": 0.5}

            avg_time_minutes = (total_time / valid_routes) / 60

            # Score: Lower time = higher score (max 10 minutes = score 1.0)
            accessibility_score = max(0.0, min(1.0, 1.0 - (avg_time_minutes / 10.0)))

            return {
                "accessibility_score": accessibility_score,
                "average_travel_time_minutes": round(avg_time_minutes, 2),
                "valid_routes": valid_routes,
            }

        except Exception as e:
            logger.error(f"Error calculating accessibility: {e}", exc_info=True)
            return {"accessibility_score": 0.5, "error": str(e)}

    def estimate_traffic_volume(
        self, latitude: float, longitude: float, road_name: Optional[str] = None
    ) -> Dict:
        """
        Estimate traffic volume for a location
        Note: Actual ADT data requires specialized APIs (TomTom, HERE)
        This provides a basic estimation based on location characteristics

        Args:
            latitude: Location latitude
            longitude: Location longitude
            road_name: Optional road name

        Returns:
            Dictionary with estimated traffic data
        """
        # Basic estimation (in production, use TomTom/HERE APIs)
        # Urban areas typically have higher traffic
        # This is a placeholder that would be replaced with actual API calls

        # Estimate based on location (urban vs suburban)
        # This is simplified - real implementation would use traffic APIs
        estimated_adt = 15000  # Default estimate
        estimated_peak_hour = 2000  # Default estimate

        # Could enhance with:
        # - Distance to major highways
        # - Population density
        # - Road classification

        return {
            "average_daily_traffic": estimated_adt,
            "peak_hour_volume": estimated_peak_hour,
            "traffic_growth_rate": 0.02,  # 2% annual growth estimate
            "source": "estimated",
            "note": "Actual ADT requires TomTom/HERE API",
        }

    def get_traffic_data_for_location(
        self, latitude: float, longitude: float, city: str, state: str
    ) -> Dict:
        """
        Get comprehensive traffic data for a location

        Args:
            latitude: Location latitude
            longitude: Location longitude
            city: City name
            state: State abbreviation

        Returns:
            Dictionary with all traffic metrics
        """
        accessibility = self.calculate_accessibility_score(
            latitude, longitude, city, state
        )
        traffic_volume = self.estimate_traffic_volume(latitude, longitude)

        return {
            **accessibility,
            **traffic_volume,
            "latitude": latitude,
            "longitude": longitude,
            "city": city,
            "state": state,
        }
