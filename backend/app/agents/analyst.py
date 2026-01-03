"""Analyst Agent - Analyzes patterns and calculates metrics"""

from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.services.llm_service import call_llm, call_llm_structured, create_agent_prompt
from app.models.schemas import PublixStore, CompetitorStore, Demographics

# from langsmith import traceable  # COMMENTED OUT: LangSmith causing 403 errors
import logging

logger = logging.getLogger(__name__)


# No-op decorator to replace @traceable
def traceable(name=None):
    def decorator(func_or_class):
        return func_or_class

    return decorator


@traceable(name="analyst_agent")
class AnalystAgent:
    """Agent responsible for analyzing data and identifying patterns"""

    def __init__(self, db: Session):
        self.db = db

    def calculate_store_density(self, state: str = None) -> Dict[str, Any]:
        """Calculate stores per capita by region"""
        logger.info(f"Calculating store density for state: {state}")

        # Query Publix stores
        query = self.db.query(PublixStore)
        if state:
            query = query.filter(PublixStore.state == state)

        stores = query.all()

        # Group by city and calculate density
        city_stats = {}
        for store in stores:
            city_key = f"{store.city}, {store.state}"
            if city_key not in city_stats:
                city_stats[city_key] = {
                    "city": store.city,
                    "state": store.state,
                    "store_count": 0,
                }
            city_stats[city_key]["store_count"] += 1

        # Get demographics and calculate per capita
        density_results = []
        for city_key, stats in city_stats.items():
            demo = (
                self.db.query(Demographics)
                .filter(
                    Demographics.city == stats["city"],
                    Demographics.state == stats["state"],
                )
                .first()
            )

            if demo and demo.population:
                per_capita = stats["store_count"] / (
                    demo.population / 100000
                )  # per 100k
                density_results.append(
                    {
                        **stats,
                        "population": demo.population,
                        "stores_per_100k": round(per_capita, 2),
                    }
                )

        return {
            "state": state,
            "total_stores": len(stores),
            "city_densities": density_results,
        }

    def identify_expansion_patterns(self, state: str) -> Dict[str, Any]:
        """Identify expansion patterns (metro → secondary cities)"""
        logger.info(f"Identifying expansion patterns for state: {state}")

        context = """You are analyzing Publix expansion patterns. Publix typically expands from
        major metro areas into secondary cities. Look for patterns where major metros have stores
        but secondary cities with similar demographics do not yet have Publix presence."""

        # Get data
        stores = self.db.query(PublixStore).filter(PublixStore.state == state).all()
        competitors = (
            self.db.query(CompetitorStore).filter(CompetitorStore.state == state).all()
        )
        demographics = (
            self.db.query(Demographics).filter(Demographics.state == state).all()
        )

        # Prepare data for LLM analysis
        store_data = [
            {
                "city": s.city,
                "latitude": s.latitude,
                "longitude": s.longitude,
                "opening_date": s.opening_date.isoformat() if s.opening_date else None,
            }
            for s in stores
        ]

        competitor_data = [
            {
                "competitor": c.competitor_name,
                "city": c.city,
                "latitude": c.latitude,
                "longitude": c.longitude,
            }
            for c in competitors
        ]

        demo_data = [
            {
                "city": d.city,
                "population": d.population,
                "median_income": d.median_income,
                "growth_rate": d.growth_rate,
            }
            for d in demographics
        ]

        task = f"""Analyze Publix expansion patterns in {state}.

Current Publix stores: {len(store_data)} stores
Competitor stores: {len(competitor_data)} stores
Demographic data: {len(demo_data)} cities

Identify:
1. Which major metros have Publix stores
2. Which secondary cities (similar population/income) don't have Publix yet
3. Expansion trajectory patterns
4. Market saturation indicators

Store locations: {store_data[:10]}...
Competitor locations: {competitor_data[:10]}...
Demographics: {demo_data[:10]}..."""

        prompt = create_agent_prompt(agent_name="Analyst", context=context, task=task)

        analysis = call_llm_structured(
            system_prompt=prompt[0]["content"], user_prompt=task
        )

        return analysis

    def compare_competitor_presence(self, state: str) -> Dict[str, Any]:
        """Compare Publix presence vs competitors"""
        logger.info(f"Comparing competitor presence in state: {state}")

        publix_stores = (
            self.db.query(PublixStore).filter(PublixStore.state == state).all()
        )
        competitor_stores = (
            self.db.query(CompetitorStore).filter(CompetitorStore.state == state).all()
        )

        # Count by competitor
        competitor_counts = {}
        for store in competitor_stores:
            name = store.competitor_name
            competitor_counts[name] = competitor_counts.get(name, 0) + 1

        # Find cities with competitors but no Publix
        competitor_cities = set(c.city for c in competitor_stores)
        publix_cities = set(s.city for s in publix_stores)
        opportunity_cities = competitor_cities - publix_cities

        return {
            "publix_store_count": len(publix_stores),
            "competitor_counts": competitor_counts,
            "opportunity_cities": list(opportunity_cities)[:20],  # Limit to 20
            "total_opportunity_cities": len(opportunity_cities),
        }

    def calculate_market_saturation(self, state: str) -> Dict[str, Any]:
        """Calculate market saturation metrics"""
        logger.info(f"Calculating market saturation for state: {state}")

        density = self.calculate_store_density(state=state)
        competitor_comparison = self.compare_competitor_presence(state=state)

        # Use LLM to synthesize saturation analysis
        context = """You are analyzing market saturation for Publix. Consider factors like:
        - Stores per capita compared to competitors
        - Population density and growth
        - Income levels
        - Geographic coverage gaps"""

        task = f"""Analyze market saturation for Publix in {state}.

Store density data: {density}
Competitor comparison: {competitor_comparison}

Provide saturation metrics and identify underserved markets."""

        prompt = create_agent_prompt(agent_name="Analyst", context=context, task=task)

        saturation_analysis = call_llm_structured(
            system_prompt=prompt[0]["content"], user_prompt=task
        )

        return {
            "density_metrics": density,
            "competitor_comparison": competitor_comparison,
            "saturation_analysis": saturation_analysis,
        }
