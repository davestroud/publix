"""Advanced Analytics API Routes"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from app.services.database import get_db
from app.services.analytics_service import AnalyticsService
from app.services.expansion_analyzer import ExpansionAnalyzer
from app.models.schemas import (
    PublixStore,
    CompetitorStore,
    Demographics,
    Prediction,
    Parcel,
)
from sqlalchemy import func, text
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/analytics/heatmap")
def get_expansion_heatmap(
    state: Optional[str] = Query(None, description="Filter by state"),
    db: Session = Depends(get_db),
):
    """Get heat map data for expansion probability by city/region"""
    try:
        analytics = AnalyticsService(db)

        # Get predictions with coordinates
        query = db.query(Prediction)
        if state:
            query = query.filter(Prediction.state == state)

        predictions = query.filter(
            Prediction.latitude.isnot(None), Prediction.longitude.isnot(None)
        ).all()

        # Get demographics for context
        demographics_query = db.query(Demographics)
        if state:
            demographics_query = demographics_query.filter(Demographics.state == state)
        demographics = demographics_query.all()

        # Build heat map data
        heatmap_data = []

        # Add predictions as heat points
        for pred in predictions:
            heatmap_data.append(
                {
                    "latitude": pred.latitude,
                    "longitude": pred.longitude,
                    "intensity": pred.confidence_score,
                    "city": pred.city,
                    "state": pred.state,
                    "type": "prediction",
                    "value": pred.confidence_score,
                }
            )

        # Add demographics as context (lower intensity)
        for demo in demographics:
            if demo.city and demo.population:
                # Calculate opportunity score based on population and growth
                opportunity_score = 0.0
                if demo.population > 50000:
                    opportunity_score += 0.3
                if demo.growth_rate and demo.growth_rate > 0.02:
                    opportunity_score += 0.2
                if demo.median_income and demo.median_income > 50000:
                    opportunity_score += 0.2

                # Get store count for saturation
                store_count = (
                    db.query(func.count(PublixStore.id))
                    .filter(
                        PublixStore.city == demo.city, PublixStore.state == demo.state
                    )
                    .scalar()
                    or 0
                )

                if store_count == 0 and opportunity_score > 0.3:
                    # High opportunity, no stores yet
                    opportunity_score += 0.3

                if opportunity_score > 0:
                    heatmap_data.append(
                        {
                            "latitude": None,  # Will need geocoding
                            "longitude": None,
                            "intensity": opportunity_score
                            * 0.5,  # Lower than predictions
                            "city": demo.city,
                            "state": demo.state,
                            "type": "opportunity",
                            "value": opportunity_score,
                            "population": demo.population,
                            "stores": store_count,
                        }
                    )

        return {
            "heatmap_points": heatmap_data,
            "total_points": len(heatmap_data),
            "state": state,
        }
    except Exception as e:
        logger.error(f"Error generating heatmap: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Heatmap generation failed: {str(e)}"
        )


@router.get("/analytics/market-saturation")
def get_market_saturation(
    state: Optional[str] = Query(None, description="Filter by state"),
    db: Session = Depends(get_db),
):
    """Get market saturation analysis by city"""
    try:
        analytics = AnalyticsService(db)

        # Get all cities with stores
        cities_query = db.query(
            PublixStore.city,
            PublixStore.state,
            func.count(PublixStore.id).label("store_count"),
        ).group_by(PublixStore.city, PublixStore.state)

        if state:
            cities_query = cities_query.filter(PublixStore.state == state)

        cities_with_stores = cities_query.all()

        saturation_data = []

        for city, state_code, store_count in cities_with_stores:
            # Get demographics
            demo = (
                db.query(Demographics)
                .filter(Demographics.city == city, Demographics.state == state_code)
                .first()
            )

            if demo and demo.population:
                # Calculate saturation metrics
                stores_per_100k = (
                    (store_count / demo.population) * 100000
                    if demo.population > 0
                    else 0
                )

                # Get competitor stores
                competitor_count = (
                    db.query(func.count(CompetitorStore.id))
                    .filter(
                        CompetitorStore.city == city,
                        CompetitorStore.state == state_code,
                    )
                    .scalar()
                    or 0
                )

                # Saturation score (0-1, higher = more saturated)
                saturation_score = min(
                    stores_per_100k / 10.0, 1.0
                )  # 10 stores per 100k = saturated

                saturation_data.append(
                    {
                        "city": city,
                        "state": state_code,
                        "publix_stores": store_count,
                        "competitor_stores": competitor_count,
                        "total_stores": store_count + competitor_count,
                        "population": demo.population,
                        "stores_per_100k": round(stores_per_100k, 2),
                        "saturation_score": round(saturation_score, 3),
                        "growth_rate": demo.growth_rate,
                        "median_income": demo.median_income,
                        "opportunity": (
                            "high"
                            if saturation_score < 0.3
                            else "medium" if saturation_score < 0.6 else "low"
                        ),
                    }
                )

        # Sort by saturation (lowest first = highest opportunity)
        saturation_data.sort(key=lambda x: x["saturation_score"])

        return {
            "saturation_analysis": saturation_data,
            "total_cities": len(saturation_data),
            "state": state,
        }
    except Exception as e:
        logger.error(f"Error calculating market saturation: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Market saturation analysis failed: {str(e)}"
        )


@router.get("/analytics/competitive-landscape")
def get_competitive_landscape(
    state: Optional[str] = Query(None, description="Filter by state"),
    db: Session = Depends(get_db),
):
    """Get competitive landscape analysis"""
    try:
        # Get competitor counts by name
        competitors_query = db.query(
            CompetitorStore.competitor_name,
            func.count(CompetitorStore.id).label("count"),
        ).group_by(CompetitorStore.competitor_name)

        if state:
            competitors_query = competitors_query.filter(CompetitorStore.state == state)

        competitor_counts = competitors_query.all()

        # Get Publix store count
        publix_query = db.query(func.count(PublixStore.id))
        if state:
            publix_query = publix_query.filter(PublixStore.state == state)
        publix_count = publix_query.scalar() or 0

        # Calculate market share
        total_stores = publix_count + sum(count for _, count in competitor_counts)

        market_share = []
        if total_stores > 0:
            market_share.append(
                {
                    "competitor": "Publix",
                    "count": publix_count,
                    "market_share": round((publix_count / total_stores) * 100, 2),
                }
            )

            for comp_name, count in competitor_counts:
                market_share.append(
                    {
                        "competitor": comp_name,
                        "count": count,
                        "market_share": round((count / total_stores) * 100, 2),
                    }
                )

        # Get overlap analysis (cities with both Publix and competitors)
        overlap_query = (
            db.query(
                PublixStore.city,
                PublixStore.state,
                func.count(func.distinct(PublixStore.id)).label("publix_count"),
                func.count(func.distinct(CompetitorStore.id)).label("competitor_count"),
            )
            .join(
                CompetitorStore,
                (PublixStore.city == CompetitorStore.city)
                & (PublixStore.state == CompetitorStore.state),
            )
            .group_by(PublixStore.city, PublixStore.state)
        )

        if state:
            overlap_query = overlap_query.filter(PublixStore.state == state)

        overlap_cities = overlap_query.all()

        return {
            "market_share": market_share,
            "total_stores": total_stores,
            "overlap_cities": [
                {
                    "city": city,
                    "state": state_code,
                    "publix_stores": publix_count,
                    "competitor_stores": comp_count,
                }
                for city, state_code, publix_count, comp_count in overlap_cities
            ],
            "total_overlap_cities": len(overlap_cities),
            "state": state,
        }
    except Exception as e:
        logger.error(f"Error analyzing competitive landscape: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Competitive analysis failed: {str(e)}"
        )


@router.get("/analytics/roi-calculator")
def calculate_roi(
    city: str = Query(..., description="City name"),
    state: str = Query(..., description="State code"),
    estimated_store_size: Optional[int] = Query(
        45000, description="Estimated store size in sq ft"
    ),
    land_cost_per_acre: Optional[float] = Query(
        500000, description="Land cost per acre"
    ),
    construction_cost_per_sqft: Optional[float] = Query(
        200, description="Construction cost per sq ft"
    ),
    db: Session = Depends(get_db),
):
    """Calculate ROI for a potential store location"""
    try:
        # Get demographics
        demo = (
            db.query(Demographics)
            .filter(Demographics.city == city, Demographics.state == state)
            .first()
        )

        if not demo:
            raise HTTPException(
                status_code=404, detail=f"Demographics not found for {city}, {state}"
            )

        # Get existing stores
        existing_stores = (
            db.query(PublixStore)
            .filter(PublixStore.city == city, PublixStore.state == state)
            .count()
        )

        # Get parcels
        parcels = (
            db.query(Parcel)
            .filter(Parcel.city == city, Parcel.state == state)
            .limit(5)
            .all()
        )

        # Calculate costs
        land_acres_needed = 20  # Typical Publix needs 15-25 acres
        land_cost = land_acres_needed * land_cost_per_acre
        construction_cost = estimated_store_size * construction_cost_per_sqft
        total_investment = land_cost + construction_cost

        # Estimate revenue (simplified model)
        # Average Publix store revenue: $30-50M annually
        # Adjust based on population and income
        base_revenue = 35000000  # $35M base

        # Adjust for population
        if demo.population:
            population_factor = min(demo.population / 100000, 2.0)  # Cap at 2x
            base_revenue *= population_factor

        # Adjust for income
        if demo.median_income:
            income_factor = demo.median_income / 50000  # Normalize to $50k
            base_revenue *= min(income_factor, 1.5)  # Cap at 1.5x

        # Reduce if stores already exist (market saturation)
        if existing_stores > 0:
            saturation_factor = 1.0 / (1.0 + existing_stores * 0.2)
            base_revenue *= saturation_factor

        estimated_annual_revenue = base_revenue

        # Calculate ROI
        # Assume 10% profit margin
        annual_profit = estimated_annual_revenue * 0.10
        roi_percentage = (annual_profit / total_investment) * 100
        payback_years = total_investment / annual_profit if annual_profit > 0 else None

        # Get prediction if exists
        prediction = (
            db.query(Prediction)
            .filter(Prediction.city == city, Prediction.state == state)
            .first()
        )

        return {
            "city": city,
            "state": state,
            "demographics": {
                "population": demo.population,
                "median_income": demo.median_income,
                "growth_rate": demo.growth_rate,
            },
            "existing_stores": existing_stores,
            "available_parcels": len(parcels),
            "costs": {
                "land_cost": land_cost,
                "construction_cost": construction_cost,
                "total_investment": total_investment,
            },
            "revenue_estimate": {
                "annual_revenue": estimated_annual_revenue,
                "annual_profit": annual_profit,
                "profit_margin": 0.10,
            },
            "roi": {
                "roi_percentage": round(roi_percentage, 2),
                "payback_years": round(payback_years, 2) if payback_years else None,
            },
            "prediction_confidence": (
                prediction.confidence_score if prediction else None
            ),
            "recommendation": (
                "high"
                if roi_percentage > 15
                else "medium" if roi_percentage > 10 else "low"
            ),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating ROI: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"ROI calculation failed: {str(e)}")


@router.get("/analytics/trends")
def get_trends(
    state: Optional[str] = Query(None, description="Filter by state"),
    years: Optional[int] = Query(5, description="Number of years to analyze"),
    db: Session = Depends(get_db),
):
    """Get trend analysis over time"""
    try:
        # Get store openings over time
        stores_query = (
            db.query(
                func.extract("year", PublixStore.opening_date).label("year"),
                func.count(PublixStore.id).label("count"),
            )
            .filter(PublixStore.opening_date.isnot(None))
            .group_by("year")
            .order_by("year")
        )

        if state:
            stores_query = stores_query.filter(PublixStore.state == state)

        store_openings = stores_query.all()

        # Get predictions over time (by creation date)
        predictions_query = (
            db.query(
                func.extract("year", Prediction.created_at).label("year"),
                func.count(Prediction.id).label("count"),
                func.avg(Prediction.confidence_score).label("avg_confidence"),
            )
            .group_by("year")
            .order_by("year")
        )

        if state:
            predictions_query = predictions_query.filter(Prediction.state == state)

        predictions_trend = predictions_query.all()

        return {
            "store_openings": [
                {
                    "year": int(year),
                    "count": count,
                }
                for year, count in store_openings
            ],
            "predictions": [
                {
                    "year": int(year),
                    "count": count,
                    "avg_confidence": float(avg_confidence) if avg_confidence else None,
                }
                for year, count, avg_confidence in predictions_trend
            ],
            "state": state,
        }
    except Exception as e:
        logger.error(f"Error analyzing trends: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Trend analysis failed: {str(e)}")
