"""
Expansion analyzer for identifying historical patterns and predicting future expansion
"""

import logging
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)


class ExpansionAnalyzer:
    """Analyzer for Publix expansion patterns and predictions"""

    def __init__(self, db: Session):
        self.db = db

    def analyze_expansion_timeline(self, state: str) -> Dict:
        """
        Analyze expansion timeline for a state

        Args:
            state: State abbreviation

        Returns:
            Dictionary with expansion timeline data
        """
        from app.models.schemas import PublixStore

        stores = (
            self.db.query(PublixStore)
            .filter_by(state=state)
            .filter(PublixStore.opening_date.isnot(None))
            .order_by(PublixStore.opening_date)
            .all()
        )

        if not stores:
            return {"error": "No stores with opening dates found"}

        # Group by year
        stores_by_year = defaultdict(list)
        cities_entered = {}
        first_store_date = None

        for store in stores:
            if store.opening_date:
                year = store.opening_date.year
                stores_by_year[year].append(store)

                # Track first store in each city
                city_key = f"{store.city},{store.state}"
                if city_key not in cities_entered:
                    cities_entered[city_key] = store.opening_date

                if not first_store_date or store.opening_date < first_store_date:
                    first_store_date = store.opening_date

        # Calculate expansion velocity
        years = sorted(stores_by_year.keys())
        if len(years) > 1:
            total_years = years[-1] - years[0] + 1
            total_stores = len(stores)
            stores_per_year = total_stores / total_years if total_years > 0 else 0
        else:
            stores_per_year = len(stores)

        return {
            "state": state,
            "first_store_date": (
                first_store_date.isoformat() if first_store_date else None
            ),
            "total_stores": len(stores),
            "stores_by_year": {
                year: len(stores_list) for year, stores_list in stores_by_year.items()
            },
            "cities_entered": len(cities_entered),
            "expansion_velocity": round(stores_per_year, 2),
            "cities_entry_sequence": {
                city: date.isoformat()
                for city, date in sorted(cities_entered.items(), key=lambda x: x[1])
            },
        }

    def identify_expansion_patterns(self) -> Dict:
        """
        Identify patterns across all states

        Returns:
            Dictionary with expansion patterns
        """
        from app.models.schemas import PublixStore

        # Get all states with stores
        states = self.db.query(PublixStore.state).distinct().all()

        patterns = {}
        for (state,) in states:
            timeline = self.analyze_expansion_timeline(state)
            patterns[state] = timeline

        # Classify states by maturity
        maturity_classification = {}
        for state, data in patterns.items():
            velocity = data.get("expansion_velocity", 0)
            total_stores = data.get("total_stores", 0)

            if total_stores > 200 and velocity < 5:
                maturity = "mature"
            elif velocity > 10:
                maturity = "expanding"
            elif velocity > 5:
                maturity = "growing"
            else:
                maturity = "emerging"

            maturity_classification[state] = maturity

        return {
            "state_patterns": patterns,
            "maturity_classification": maturity_classification,
        }

    def predict_next_expansion_cities(self, state: str, top_n: int = 10) -> List[Dict]:
        """
        Predict which cities Publix is likely to expand into next

        Args:
            state: State abbreviation
            top_n: Number of top predictions to return

        Returns:
            List of predicted cities with reasoning
        """
        from app.models.schemas import Demographics
        from app.services.analytics_service import AnalyticsService

        analytics = AnalyticsService(self.db)

        # Get expansion opportunities
        opportunities = analytics.identify_expansion_opportunities(state)

        # Enhance with historical patterns
        timeline = self.analyze_expansion_timeline(state)
        existing_cities = set(
            city.split(",")[0]
            for city in timeline.get("cities_entry_sequence", {}).keys()
        )

        predictions = []
        for opp in opportunities[:top_n]:
            city = opp["city"]

            # Skip if already has stores
            if city in existing_cities:
                continue

            # Build reasoning
            reasoning_factors = []
            if opp["saturation_score"] < 0.3:
                reasoning_factors.append("Low market saturation")
            if opp["population"] > 100000:
                reasoning_factors.append("Large population base")
            if opp["stores_per_100k"] < 1.0:
                reasoning_factors.append("Under-served market")

            predictions.append(
                {
                    "city": city,
                    "state": state,
                    "population": opp["population"],
                    "current_stores": opp["publix_stores"],
                    "opportunity_score": opp["opportunity_score"],
                    "reasoning_factors": reasoning_factors,
                    "confidence": min(opp["opportunity_score"] * 1.2, 1.0),
                }
            )

        return predictions

    def compare_to_similar_markets(self, target_city: str, target_state: str) -> Dict:
        """
        Compare target city to similar markets where Publix has expanded

        Args:
            target_city: City to analyze
            target_state: State abbreviation

        Returns:
            Dictionary with comparison data
        """
        from app.models.schemas import Demographics, PublixStore
        from app.services.analytics_service import AnalyticsService

        analytics = AnalyticsService(self.db)

        # Get target city demographics
        target_demo = (
            self.db.query(Demographics)
            .filter_by(city=target_city, state=target_state)
            .first()
        )

        if not target_demo or not target_demo.population:
            return {"error": "No demographics data for target city"}

        # Find similar cities (similar population, same state or adjacent states)
        similar_cities = (
            self.db.query(Demographics)
            .filter(
                Demographics.population.between(
                    target_demo.population * 0.7, target_demo.population * 1.3
                )
            )
            .all()
        )

        # Get Publix presence in similar cities
        comparisons = []
        for city_demo in similar_cities:
            store_count = (
                self.db.query(PublixStore)
                .filter_by(city=city_demo.city, state=city_demo.state)
                .count()
            )

            if store_count > 0:  # Only include cities with Publix
                comparisons.append(
                    {
                        "city": city_demo.city,
                        "state": city_demo.state,
                        "population": city_demo.population,
                        "publix_stores": store_count,
                        "stores_per_100k": (
                            store_count / city_demo.population * 100000
                            if city_demo.population > 0
                            else 0
                        ),
                    }
                )

        # Calculate target city metrics
        target_metrics = analytics.calculate_store_density(target_city, target_state)

        return {
            "target_city": target_city,
            "target_state": target_state,
            "target_population": target_demo.population,
            "target_stores": (
                target_metrics.get("publix_stores", 0) if target_metrics else 0
            ),
            "similar_markets": comparisons,
            "average_stores_in_similar": (
                sum(c["publix_stores"] for c in comparisons) / len(comparisons)
                if comparisons
                else 0
            ),
        }
