"""Site Evaluator Agent - Evaluates specific parcels for suitability"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.services.llm_service import call_llm_structured, create_agent_prompt
from app.models.schemas import ZoningRecord, PublixStore, CompetitorStore, Demographics

# from langsmith import traceable  # COMMENTED OUT: LangSmith causing 403 errors
import math
import logging

logger = logging.getLogger(__name__)


# No-op decorator to replace @traceable
def traceable(name=None):
    def decorator(func_or_class):
        return func_or_class

    return decorator


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two points in miles using Haversine formula"""
    R = 3959  # Earth radius in miles

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


@traceable(name="site_evaluator_agent")
class SiteEvaluatorAgent:
    """Agent responsible for evaluating specific parcels and sites"""

    def __init__(self, db: Session):
        self.db = db

    def evaluate_parcel(
        self,
        parcel_id: str,
        latitude: float,
        longitude: float,
        acreage: float,
        city: str,
        state: str,
    ) -> Dict[str, Any]:
        """Evaluate a specific parcel for Publix suitability"""
        logger.info(f"Evaluating parcel {parcel_id} in {city}, {state}")

        # Check zoning compatibility
        zoning = (
            self.db.query(ZoningRecord)
            .filter(ZoningRecord.parcel_id == parcel_id)
            .first()
        )

        # Get nearby stores
        nearby_publix = self._find_nearby_stores(
            latitude, longitude, PublixStore, max_distance=10.0
        )
        nearby_competitors = self._find_nearby_stores(
            latitude, longitude, CompetitorStore, max_distance=10.0
        )

        # Get demographics
        demographics = (
            self.db.query(Demographics)
            .filter(Demographics.city == city, Demographics.state == state)
            .first()
        )

        # Use LLM to evaluate
        context = """You are evaluating a commercial parcel for Publix store development.
        Consider: acreage (15-25 acres ideal), zoning status, proximity to competitors,
        demographic fit, and market opportunity."""

        evaluation_data = {
            "parcel_id": parcel_id,
            "location": {
                "city": city,
                "state": state,
                "lat": latitude,
                "lng": longitude,
            },
            "acreage": acreage,
            "zoning_status": zoning.zoning_status if zoning else "unknown",
            "nearby_publix_stores": len(nearby_publix),
            "nearby_competitors": len(nearby_competitors),
            "demographics": (
                {
                    "population": demographics.population if demographics else None,
                    "median_income": (
                        demographics.median_income if demographics else None
                    ),
                    "growth_rate": demographics.growth_rate if demographics else None,
                }
                if demographics
                else None
            ),
        }

        task = f"""Evaluate this parcel for Publix store development:

{evaluation_data}

Provide:
1. Suitability score (0-100)
2. Key strengths
3. Key concerns
4. Recommendations"""

        evaluation = call_llm_structured(system_prompt=context, user_prompt=task)

        return {
            "parcel_id": parcel_id,
            "evaluation_data": evaluation_data,
            "evaluation": evaluation,
        }

    def evaluate_city(self, city: str, state: str) -> Dict[str, Any]:
        """Evaluate a city for Publix expansion potential"""
        logger.info(f"Evaluating city {city}, {state}")

        # Get existing stores
        existing_stores = (
            self.db.query(PublixStore)
            .filter(PublixStore.city == city, PublixStore.state == state)
            .all()
        )

        # Get competitors
        competitors = (
            self.db.query(CompetitorStore)
            .filter(CompetitorStore.city == city, CompetitorStore.state == state)
            .all()
        )

        # Get demographics
        demographics = (
            self.db.query(Demographics)
            .filter(Demographics.city == city, Demographics.state == state)
            .first()
        )

        # Get available parcels
        parcels = (
            self.db.query(ZoningRecord)
            .filter(
                ZoningRecord.city == city,
                ZoningRecord.state == state,
                ZoningRecord.acreage >= 15.0,
                ZoningRecord.acreage <= 25.0,
            )
            .all()
        )

        context = """You are evaluating a city for Publix expansion potential.
        Consider: existing Publix presence, competitor density, demographics,
        available commercial parcels, and market opportunity."""

        city_data = {
            "city": city,
            "state": state,
            "existing_publix_stores": len(existing_stores),
            "competitor_stores": len(competitors),
            "available_parcels": len(parcels),
            "demographics": (
                {
                    "population": demographics.population if demographics else None,
                    "median_income": (
                        demographics.median_income if demographics else None
                    ),
                    "growth_rate": demographics.growth_rate if demographics else None,
                }
                if demographics
                else None
            ),
        }

        task = f"""Evaluate {city}, {state} for Publix expansion:

{city_data}

Provide:
1. Expansion potential score (0-100)
2. Market opportunity assessment
3. Key factors supporting expansion
4. Risks or concerns
5. Recommended next steps"""

        evaluation = call_llm_structured(system_prompt=context, user_prompt=task)

        return {
            "city": city,
            "state": state,
            "city_data": city_data,
            "evaluation": evaluation,
        }

    def _find_nearby_stores(
        self, latitude: float, longitude: float, store_model, max_distance: float = 10.0
    ) -> List:
        """Find stores within max_distance miles"""
        all_stores = self.db.query(store_model).all()
        nearby = []

        for store in all_stores:
            if store.latitude and store.longitude:
                distance = calculate_distance(
                    latitude, longitude, store.latitude, store.longitude
                )
                if distance <= max_distance:
                    nearby.append(store)

        return nearby

    def evaluate_zoning_compatibility(
        self, zoning_record: ZoningRecord
    ) -> Dict[str, Any]:
        """Evaluate if zoning record is compatible with Publix development"""
        logger.info(f"Evaluating zoning compatibility for record {zoning_record.id}")

        context = """You are evaluating zoning records for Publix store development.
        Publix typically needs: commercial zoning, 15-25 acre parcels, good access,
        visibility, and proximity to residential areas."""

        task = f"""Evaluate this zoning record for Publix compatibility:

Location: {zoning_record.city}, {zoning_record.state}
Acreage: {zoning_record.acreage} acres
Zoning Status: {zoning_record.zoning_status}
Permit Type: {zoning_record.permit_type}
Description: {zoning_record.description[:500] if zoning_record.description else 'N/A'}

Provide compatibility assessment."""

        evaluation = call_llm_structured(system_prompt=context, user_prompt=task)

        return {"zoning_record_id": zoning_record.id, "evaluation": evaluation}
