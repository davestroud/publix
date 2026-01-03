"""
Analytics service for calculating store density, market saturation, and expansion metrics
"""

import logging
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func
import math

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for calculating store analytics and market metrics"""

    def __init__(self, db: Session):
        self.db = db

    def calculate_store_density(self, city: str, state: str) -> Optional[Dict]:
        """
        Calculate store density metrics for a city

        Args:
            city: City name
            state: State abbreviation

        Returns:
            Dictionary with density metrics
        """
        from app.models.schemas import PublixStore, CompetitorStore, Demographics

        # Get demographics
        demo = self.db.query(Demographics).filter_by(city=city, state=state).first()
        if not demo or not demo.population:
            logger.warning(f"No demographics data for {city}, {state}")
            return None

        # Count Publix stores in city
        publix_count = (
            self.db.query(PublixStore).filter_by(city=city, state=state).count()
        )

        # Count competitor stores
        walmart_count = (
            self.db.query(CompetitorStore)
            .filter_by(city=city, state=state, competitor_name="Walmart")
            .count()
        )
        kroger_count = (
            self.db.query(CompetitorStore)
            .filter_by(city=city, state=state, competitor_name="Kroger")
            .count()
        )

        # Calculate stores per 100K population
        stores_per_100k = (
            (publix_count / demo.population * 100000) if demo.population > 0 else 0
        )

        # Calculate stores per square mile (rough estimate using city area)
        # Using average city density: ~3,000 people per square mile for typical US city
        estimated_sq_miles = demo.population / 3000 if demo.population > 0 else 0
        stores_per_sq_mile = (
            publix_count / estimated_sq_miles if estimated_sq_miles > 0 else 0
        )

        # Calculate market saturation score (0-1, higher = more saturated)
        # Based on stores per capita compared to mature markets
        # Florida average: ~1 store per 50K people = saturation score 1.0
        baseline_stores_per_100k = 2.0  # Baseline for "mature" market
        saturation_score = min(stores_per_100k / baseline_stores_per_100k, 1.0)

        metrics = {
            "publix_stores": publix_count,
            "walmart_stores": walmart_count,
            "kroger_stores": kroger_count,
            "total_competitor_stores": walmart_count + kroger_count,
            "stores_per_100k": round(stores_per_100k, 2),
            "stores_per_sq_mile": round(stores_per_sq_mile, 4),
            "saturation_score": round(saturation_score, 3),
            "population": demo.population,
        }

        return metrics

    def calculate_nearest_competitor_distance(
        self, latitude: float, longitude: float, city: str, state: str
    ) -> Optional[Dict]:
        """
        Calculate distance to nearest competitor stores

        Args:
            latitude: Store latitude
            longitude: Store longitude
            city: City name
            state: State abbreviation

        Returns:
            Dictionary with distances to nearest competitors
        """
        from app.models.schemas import CompetitorStore

        # Get all competitor stores in the state
        competitors = self.db.query(CompetitorStore).filter_by(state=state).all()

        if not competitors:
            return None

        distances = {}
        for competitor in competitors:
            if competitor.latitude and competitor.longitude:
                distance = self._haversine_distance(
                    latitude, longitude, competitor.latitude, competitor.longitude
                )
                comp_name = competitor.competitor_name

                if comp_name not in distances or distance < distances[comp_name]:
                    distances[comp_name] = round(distance, 2)

        return distances

    def calculate_market_saturation_by_state(self, state: str) -> Dict:
        """
        Calculate market saturation metrics for all cities in a state

        Args:
            state: State abbreviation

        Returns:
            Dictionary with saturation metrics by city
        """
        from app.models.schemas import Demographics

        cities = self.db.query(Demographics).filter_by(state=state).all()
        results = {}

        for demo in cities:
            metrics = self.calculate_store_density(demo.city, demo.state)
            if metrics:
                results[demo.city] = metrics

        return results

    def identify_expansion_opportunities(
        self, state: str, min_population: int = 50000
    ) -> List[Dict]:
        """
        Identify cities with expansion opportunities based on low saturation

        Args:
            state: State abbreviation
            min_population: Minimum population to consider

        Returns:
            List of cities ranked by expansion opportunity
        """
        from app.models.schemas import Demographics

        cities = (
            self.db.query(Demographics)
            .filter_by(state=state)
            .filter(Demographics.population >= min_population)
            .all()
        )

        opportunities = []
        for demo in cities:
            metrics = self.calculate_store_density(demo.city, demo.state)
            if not metrics:
                continue

            # Calculate opportunity score (inverse of saturation)
            opportunity_score = 1.0 - metrics["saturation_score"]

            # Weight by population (larger cities = higher priority)
            population_weight = (
                min(demo.population / 100000, 1.0) if demo.population else 0
            )

            # Combined score
            combined_score = opportunity_score * 0.7 + population_weight * 0.3

            opportunities.append(
                {
                    "city": demo.city,
                    "state": demo.state,
                    "population": demo.population,
                    "publix_stores": metrics["publix_stores"],
                    "stores_per_100k": metrics["stores_per_100k"],
                    "saturation_score": metrics["saturation_score"],
                    "opportunity_score": round(combined_score, 3),
                }
            )

        # Sort by opportunity score (highest first)
        opportunities.sort(key=lambda x: x["opportunity_score"], reverse=True)
        return opportunities

    def _haversine_distance(
        self, lat1: float, lon1: float, lat2: float, lon2: float
    ) -> float:
        """
        Calculate distance between two points using Haversine formula

        Returns:
            Distance in miles
        """
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

    def update_demographics_metrics(self, city: str, state: str) -> bool:
        """
        Update demographics record with calculated metrics

        Args:
            city: City name
            state: State abbreviation

        Returns:
            True if updated successfully
        """
        from app.models.schemas import Demographics

        demo = self.db.query(Demographics).filter_by(city=city, state=state).first()
        if not demo:
            return False

        metrics = self.calculate_store_density(city, state)
        if not metrics:
            return False

        # Update stores_per_capita
        demo.stores_per_capita = metrics["stores_per_100k"]

        # Update additional_data with saturation metrics
        if not demo.additional_data:
            demo.additional_data = {}

        demo.additional_data.update(
            {
                "saturation_score": metrics["saturation_score"],
                "stores_per_sq_mile": metrics["stores_per_sq_mile"],
                "competitor_stores": {
                    "walmart": metrics["walmart_stores"],
                    "kroger": metrics["kroger_stores"],
                },
            }
        )

        try:
            self.db.commit()
            logger.info(f"Updated metrics for {city}, {state}")
            return True
        except Exception as e:
            logger.error(f"Failed to update metrics: {e}")
            self.db.rollback()
            return False
