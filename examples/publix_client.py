"""
Python client for Publix Expansion Predictor API

Usage:
    from publix_client import PublixExpansionClient

    client = PublixExpansionClient()
    stats = client.get_dashboard_stats()
    predictions = client.get_predictions(state="KY", min_confidence=0.8)
"""

import requests
from typing import List, Dict, Optional


class PublixExpansionClient:
    """Client for interacting with the Publix Expansion Predictor API"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize the client

        Args:
            base_url: Base URL of the API (default: http://localhost:8000)
        """
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

    def get_dashboard_stats(self) -> Dict:
        """Get dashboard statistics"""
        response = self.session.get(f"{self.base_url}/api/dashboard/stats")
        response.raise_for_status()
        return response.json()

    def get_stores(
        self, state: Optional[str] = None, city: Optional[str] = None, limit: int = 100
    ) -> List[Dict]:
        """
        Get Publix stores

        Args:
            state: Filter by state code (e.g., "KY")
            city: Filter by city name
            limit: Maximum number of results (1-1000)

        Returns:
            List of store dictionaries
        """
        params = {"limit": limit}
        if state:
            params["state"] = state
        if city:
            params["city"] = city

        response = self.session.get(f"{self.base_url}/api/stores", params=params)
        response.raise_for_status()
        return response.json()

    def get_predictions(
        self,
        state: Optional[str] = None,
        city: Optional[str] = None,
        min_confidence: Optional[float] = None,
        limit: int = 100,
    ) -> List[Dict]:
        """
        Get predictions for new store locations

        Args:
            state: Filter by state code
            city: Filter by city name
            min_confidence: Minimum confidence score (0.0-1.0)
            limit: Maximum number of results

        Returns:
            List of prediction dictionaries
        """
        params = {"limit": limit}
        if state:
            params["state"] = state
        if city:
            params["city"] = city
        if min_confidence is not None:
            params["min_confidence"] = min_confidence

        response = self.session.get(f"{self.base_url}/api/predictions", params=params)
        response.raise_for_status()
        return response.json()

    def analyze_region(
        self, region: str, cities: Optional[List[Dict[str, str]]] = None
    ) -> Dict:
        """
        Run analysis for a region (state or region name)

        Args:
            region: State code or region name (e.g., "KY")
            cities: Optional list of specific cities to evaluate
                   Format: [{"city": "Lexington", "state": "KY"}, ...]

        Returns:
            Analysis results dictionary
        """
        payload = {"region": region}
        if cities:
            payload["cities"] = cities

        response = self.session.post(f"{self.base_url}/api/analyze", json=payload)
        response.raise_for_status()
        return response.json()

    def analyze_city(self, city: str, state: str) -> Dict:
        """
        Analyze a single city for expansion potential

        Args:
            city: City name
            state: State code

        Returns:
            City analysis dictionary
        """
        payload = {"city": city, "state": state}
        response = self.session.post(f"{self.base_url}/api/analyze/city", json=payload)
        response.raise_for_status()
        return response.json()

    def get_demographics(self, city: str, state: str) -> Dict:
        """
        Get demographic data for a city

        Args:
            city: City name
            state: State code

        Returns:
            Demographics dictionary
        """
        response = self.session.get(
            f"{self.base_url}/api/demographics/{city}", params={"state": state}
        )
        response.raise_for_status()
        return response.json()

    def get_zoning_records(
        self,
        region: str,
        city: Optional[str] = None,
        min_acreage: float = 15.0,
        max_acreage: float = 25.0,
        limit: int = 100,
    ) -> List[Dict]:
        """
        Get zoning records for a region

        Args:
            region: State code or "city,state" format
            city: Optional city filter
            min_acreage: Minimum parcel size in acres
            max_acreage: Maximum parcel size in acres
            limit: Maximum number of results

        Returns:
            List of zoning record dictionaries
        """
        params = {
            "min_acreage": min_acreage,
            "max_acreage": max_acreage,
            "limit": limit,
        }
        if city:
            params["city"] = city

        response = self.session.get(
            f"{self.base_url}/api/zoning/{region}", params=params
        )
        response.raise_for_status()
        return response.json()


# Example usage
if __name__ == "__main__":
    # Initialize client
    client = PublixExpansionClient()

    print("=== Publix Expansion Predictor API Client ===\n")

    # Get dashboard stats
    print("1. Getting dashboard statistics...")
    stats = client.get_dashboard_stats()
    print(f"   Total stores: {stats['total_stores']}")
    print(f"   Total predictions: {stats['total_predictions']}")
    print(f"   Average confidence: {stats['average_confidence']:.2%}\n")

    # Get stores
    print("2. Getting stores in Kentucky...")
    stores = client.get_stores(state="KY")
    print(f"   Found {len(stores)} stores\n")

    # Get predictions
    print("3. Getting high-confidence predictions...")
    predictions = client.get_predictions(state="KY", min_confidence=0.8)
    print(f"   Found {len(predictions)} predictions\n")

    if predictions:
        print("   Top predictions:")
        for i, pred in enumerate(predictions[:3], 1):
            print(
                f"   {i}. {pred['city']}, {pred['state']}: {pred['confidence_score']:.2%}"
            )

    print("\n✅ Client test complete!")
