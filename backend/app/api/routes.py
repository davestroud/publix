"""FastAPI routes"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from app.services.database import get_db
from app.models.schemas import (
    PublixStore,
    CompetitorStore,
    Prediction,
    Demographics,
    ZoningRecord,
    Parcel,
    AnalysisRun,
    ShoppingCenter,
    TrafficData,
    NewsArticle,
    EconomicIndicator,
    DevelopmentProject,
)
from sqlalchemy import func
from app.api.models import (
    StoreResponse,
    PredictionResponse,
    AnalysisRequest,
    AnalysisResponse,
    CityAnalysisRequest,
    DemographicsResponse,
    ZoningRecordResponse,
    DashboardStatsResponse,
    ChatRequest,
    ChatResponse,
)
from app.api import analytics_routes
from app.agents.orchestrator import Orchestrator
from app.agents.reporter import ReporterAgent
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/stores", response_model=List[StoreResponse])
def get_stores(
    state: Optional[str] = Query(None, description="Filter by state"),
    city: Optional[str] = Query(None, description="Filter by city"),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """Get list of Publix stores"""
    query = db.query(PublixStore)

    if state:
        query = query.filter(PublixStore.state == state)
    if city:
        query = query.filter(PublixStore.city == city)

    stores = query.limit(limit).all()
    return stores


@router.get("/predictions", response_model=List[PredictionResponse])
def get_predictions(
    state: Optional[str] = Query(None, description="Filter by state"),
    city: Optional[str] = Query(None, description="Filter by city"),
    min_confidence: Optional[float] = Query(
        None, ge=0.0, le=1.0, description="Minimum confidence score"
    ),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """Get predictions for new store locations"""
    query = db.query(Prediction)

    if state:
        query = query.filter(Prediction.state == state)
    if city:
        query = query.filter(Prediction.city == city)
    if min_confidence is not None:
        query = query.filter(Prediction.confidence_score >= min_confidence)

    predictions = query.order_by(Prediction.confidence_score.desc()).limit(limit).all()
    return predictions


@router.post("/analyze", response_model=AnalysisResponse)
def trigger_analysis(request: AnalysisRequest, db: Session = Depends(get_db)):
    """Trigger new analysis for a region"""
    try:
        orchestrator = Orchestrator(db)
        results = orchestrator.run_analysis(
            region=request.region, cities=request.cities
        )
        return results
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/analyze/city")
def analyze_city(request: CityAnalysisRequest, db: Session = Depends(get_db)):
    """Analyze a single city for expansion potential"""
    try:
        orchestrator = Orchestrator(db)
        results = orchestrator.analyze_single_city(
            city=request.city, state=request.state
        )
        return results
    except Exception as e:
        logger.error(f"City analysis failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"City analysis failed: {str(e)}")


@router.get("/demographics", response_model=List[DemographicsResponse])
def get_demographics_list(
    state: Optional[str] = Query(None, description="Filter by state"),
    city: Optional[str] = Query(None, description="Filter by city"),
    limit: int = Query(500, ge=1, le=5000),
    db: Session = Depends(get_db),
):
    """Get list of demographic records"""
    query = db.query(Demographics)

    if state:
        query = query.filter(Demographics.state == state)
    if city:
        query = query.filter(Demographics.city == city)

    demographics = query.limit(limit).all()
    return demographics


@router.get("/demographics/{city}", response_model=Optional[DemographicsResponse])
def get_demographics(
    city: str,
    state: str = Query(..., description="State code"),
    db: Session = Depends(get_db),
):
    """Get demographic data for a city"""
    demographics = (
        db.query(Demographics)
        .filter(Demographics.city == city, Demographics.state == state)
        .first()
    )

    if not demographics:
        raise HTTPException(status_code=404, detail="Demographics not found")

    return demographics


@router.get("/zoning/{region}", response_model=List[ZoningRecordResponse])
def get_zoning_records(
    region: str,
    city: Optional[str] = Query(None, description="Filter by city"),
    min_acreage: Optional[float] = Query(15.0, ge=0.0, description="Minimum acreage"),
    max_acreage: Optional[float] = Query(25.0, ge=0.0, description="Maximum acreage"),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """Get zoning records for a region"""
    query = db.query(ZoningRecord)

    # Parse region - could be state or city,state
    if "," in region:
        parts = region.split(",")
        city_filter = parts[0].strip()
        state_filter = parts[1].strip() if len(parts) > 1 else None
        query = query.filter(ZoningRecord.city == city_filter)
        if state_filter:
            query = query.filter(ZoningRecord.state == state_filter)
    else:
        query = query.filter(ZoningRecord.state == region)

    if city:
        query = query.filter(ZoningRecord.city == city)
    if min_acreage:
        query = query.filter(ZoningRecord.acreage >= min_acreage)
    if max_acreage:
        query = query.filter(ZoningRecord.acreage <= max_acreage)

    records = query.limit(limit).all()
    return records


@router.get("/competitors", response_model=List[Dict])
def get_competitor_stores(
    state: Optional[str] = Query(None, description="Filter by state"),
    competitor_name: Optional[str] = Query(
        None, description="Filter by competitor name"
    ),
    limit: int = Query(1000, ge=1, le=5000),
    db: Session = Depends(get_db),
):
    """Get competitor stores"""
    query = db.query(CompetitorStore)

    if state:
        query = query.filter(CompetitorStore.state == state)
    if competitor_name:
        query = query.filter(CompetitorStore.competitor_name == competitor_name)

    stores = query.limit(limit).all()
    return [
        {
            "id": s.id,
            "competitor_name": s.competitor_name,
            "address": s.address,
            "city": s.city,
            "state": s.state,
            "zip_code": s.zip_code,
            "latitude": s.latitude,
            "longitude": s.longitude,
        }
        for s in stores
    ]


@router.get("/parcels", response_model=List[Dict])
def get_parcels(
    city: Optional[str] = Query(None, description="Filter by city"),
    state: Optional[str] = Query(None, description="Filter by state"),
    min_acreage: Optional[float] = Query(15.0, ge=0.0, description="Minimum acreage"),
    max_acreage: Optional[float] = Query(25.0, ge=0.0, description="Maximum acreage"),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """Get parcels matching criteria"""
    query = db.query(Parcel)

    if city:
        query = query.filter(Parcel.city == city)
    if state:
        query = query.filter(Parcel.state == state)
    if min_acreage:
        query = query.filter(Parcel.acreage >= min_acreage)
    if max_acreage:
        query = query.filter(Parcel.acreage <= max_acreage)

    parcels = query.limit(limit).all()
    return [
        {
            "id": p.id,
            "parcel_id": p.parcel_id,
            "address": p.address,
            "city": p.city,
            "state": p.state,
            "acreage": p.acreage,
            "current_zoning": p.current_zoning,
            "assessed_value": p.assessed_value,
            "land_use_code": p.land_use_code,
            "latitude": p.latitude,
            "longitude": p.longitude,
            "owner_name": p.owner_name,
            "owner_type": p.owner_type,
            "additional_data": p.additional_data,
        }
        for p in parcels
    ]


@router.post("/smarty/geocode")
def geocode_address(
    address: str = Query(..., description="Street address"),
    city: str = Query(..., description="City name"),
    state: str = Query(..., description="State abbreviation"),
    zip_code: Optional[str] = Query(None, description="ZIP code"),
):
    """Geocode an address using Smarty API"""
    try:
        from app.services.smarty_service import SmartyService

        smarty = SmartyService()
        if not smarty.available:
            raise HTTPException(status_code=503, detail="Smarty API not configured")

        result = smarty.geocode_address(address, city, state, zip_code)
        if not result:
            raise HTTPException(status_code=404, detail="Address not found")

        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Geocoding failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Geocoding failed: {str(e)}")


@router.post("/smarty/property")
def get_property_data(
    address: str = Query(..., description="Street address"),
    city: str = Query(..., description="City name"),
    state: str = Query(..., description="State abbreviation"),
    zip_code: Optional[str] = Query(None, description="ZIP code"),
):
    """Get property data for an address using Smarty API"""
    try:
        from app.services.smarty_service import SmartyService

        smarty = SmartyService()
        if not smarty.available:
            raise HTTPException(status_code=503, detail="Smarty API not configured")

        result = smarty.get_property_by_address(address, city, state, zip_code)
        if not result:
            raise HTTPException(status_code=404, detail="Property data not found")

        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Property lookup failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Property lookup failed: {str(e)}")


@router.post("/smarty/search-parcels")
def search_parcels_smarty(
    city: str = Query(..., description="City name"),
    state: str = Query(..., description="State abbreviation"),
    min_acreage: float = Query(15.0, ge=0.0, description="Minimum acreage"),
    max_acreage: float = Query(25.0, ge=0.0, description="Maximum acreage"),
    db: Session = Depends(get_db),
):
    """Search for parcels in a city using Smarty API"""
    try:
        from app.services.parcel_service import ParcelService

        parcel_service = ParcelService(db=db)
        parcels = parcel_service.get_parcels_by_city(
            city=city,
            state=state,
            min_acreage=min_acreage,
            max_acreage=max_acreage,
        )

        return {
            "city": city,
            "state": state,
            "parcels": parcels,
            "count": len(parcels),
        }
    except Exception as e:
        logger.error(f"Parcel search failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Parcel search failed: {str(e)}")


@router.get("/dashboard/stats", response_model=DashboardStatsResponse)
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics with enhanced data"""
    reporter = ReporterAgent(db)
    stats = reporter.generate_dashboard_summary()

    # Add additional stats
    total_competitors = db.query(CompetitorStore).count()
    total_demographics = db.query(Demographics).count()
    total_parcels = db.query(Parcel).count()
    total_zoning_records = db.query(ZoningRecord).count()

    # Stores by state
    stores_by_state = (
        db.query(PublixStore.state, func.count(PublixStore.id))
        .group_by(PublixStore.state)
        .all()
    )

    # Competitors by type
    competitors_by_type = (
        db.query(CompetitorStore.competitor_name, func.count(CompetitorStore.id))
        .group_by(CompetitorStore.competitor_name)
        .all()
    )

    # Demographics by state
    demographics_by_state = (
        db.query(Demographics.state, func.count(Demographics.id))
        .group_by(Demographics.state)
        .all()
    )

    # Parcels by state
    parcels_by_state = (
        db.query(Parcel.state, func.count(Parcel.id)).group_by(Parcel.state).all()
    )

    return {
        **stats,
        "total_competitors": total_competitors,
        "total_demographics": total_demographics,
        "total_parcels": total_parcels,
        "total_zoning_records": total_zoning_records,
        "stores_by_state": {state: count for state, count in stores_by_state},
        "competitors_by_type": {name: count for name, count in competitors_by_type},
        "demographics_by_state": {
            state: count for state, count in demographics_by_state
        },
        "parcels_by_state": {state: count for state, count in parcels_by_state},
    }


@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(
    request: ChatRequest,
    db: Session = Depends(get_db),
):
    """Chat endpoint for LLM-powered queries about Publix expansion data"""
    try:
        from app.services.chat_service import ChatService

        chat_service = ChatService(db)
        result = chat_service.chat_with_data(
            request.message, request.conversation_history
        )
        return result
    except ImportError:
        raise HTTPException(
            status_code=503,
            detail="OpenAI not available. Install with: poetry add openai",
        )
    except ValueError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Chat error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


@router.post("/chat/simple", response_model=ChatResponse)
def chat_simple(
    message: str = Query(..., description="User message"),
    db: Session = Depends(get_db),
):
    """Simple chat endpoint without conversation history"""
    try:
        from app.services.chat_service import ChatService

        chat_service = ChatService(db)
        result = chat_service.chat_with_data(message)
        return result
    except ImportError:
        raise HTTPException(
            status_code=503,
            detail="OpenAI not available. Install with: poetry add openai",
        )
    except ValueError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Chat error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


@router.get("/shopping-centers", response_model=List[Dict])
def get_shopping_centers(
    state: Optional[str] = Query(None, description="Filter by state"),
    city: Optional[str] = Query(None, description="Filter by city"),
    min_co_tenancy_score: Optional[float] = Query(None, ge=0.0, le=100.0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """Get shopping centers with co-tenancy data"""
    query = db.query(ShoppingCenter)

    if state:
        query = query.filter(ShoppingCenter.state == state)
    if city:
        query = query.filter(ShoppingCenter.city == city)
    if min_co_tenancy_score is not None:
        query = query.filter(ShoppingCenter.co_tenancy_score >= min_co_tenancy_score)

    centers = query.order_by(ShoppingCenter.co_tenancy_score.desc()).limit(limit).all()
    return [
        {
            "id": c.id,
            "name": c.name,
            "address": c.address,
            "city": c.city,
            "state": c.state,
            "latitude": c.latitude,
            "longitude": c.longitude,
            "rating": c.rating,
            "anchor_tenants": c.anchor_tenants,
            "co_tenancy_score": c.co_tenancy_score,
            "occupancy_rate": c.occupancy_rate,
            "additional_data": c.additional_data,
        }
        for c in centers
    ]


@router.get("/traffic-data", response_model=List[Dict])
def get_traffic_data(
    state: Optional[str] = Query(None, description="Filter by state"),
    city: Optional[str] = Query(None, description="Filter by city"),
    min_accessibility_score: Optional[float] = Query(None, ge=0.0, le=1.0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """Get traffic and accessibility data"""
    query = db.query(TrafficData)

    if state:
        query = query.filter(TrafficData.state == state)
    if city:
        query = query.filter(TrafficData.city == city)
    if min_accessibility_score is not None:
        query = query.filter(TrafficData.accessibility_score >= min_accessibility_score)

    traffic = query.order_by(TrafficData.accessibility_score.desc()).limit(limit).all()
    return [
        {
            "id": t.id,
            "location_id": t.location_id,
            "location_type": t.location_type,
            "city": t.city,
            "state": t.state,
            "latitude": t.latitude,
            "longitude": t.longitude,
            "average_daily_traffic": t.average_daily_traffic,
            "peak_hour_volume": t.peak_hour_volume,
            "traffic_growth_rate": t.traffic_growth_rate,
            "accessibility_score": t.accessibility_score,
            "source": t.source,
        }
        for t in traffic
    ]


@router.get("/news", response_model=List[Dict])
def get_news_articles(
    state: Optional[str] = Query(None, description="Filter by state"),
    city: Optional[str] = Query(None, description="Filter by city"),
    topic: Optional[str] = Query(None, description="Filter by topic"),
    sentiment: Optional[str] = Query(None, description="Filter by sentiment"),
    mentions_publix: Optional[bool] = Query(
        None, description="Filter by Publix mentions"
    ),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """Get news articles about Publix and competitors"""
    query = db.query(NewsArticle)

    if state:
        query = query.filter(NewsArticle.state == state)
    if city:
        query = query.filter(NewsArticle.city == city)
    if topic:
        query = query.filter(NewsArticle.topic == topic)
    if sentiment:
        query = query.filter(NewsArticle.sentiment == sentiment)
    if mentions_publix is not None:
        query = query.filter(NewsArticle.mentions_publix == mentions_publix)

    articles = query.order_by(NewsArticle.published_date.desc()).limit(limit).all()
    return [
        {
            "id": a.id,
            "title": a.title,
            "content": a.content,
            "source": a.source,
            "url": a.url,
            "published_date": (
                a.published_date.isoformat() if a.published_date else None
            ),
            "city": a.city,
            "state": a.state,
            "topic": a.topic,
            "sentiment": a.sentiment,
            "mentions_publix": a.mentions_publix,
            "mentions_competitor": a.mentions_competitor,
            "relevance_score": a.relevance_score,
        }
        for a in articles
    ]


@router.get("/economic-indicators", response_model=List[Dict])
def get_economic_indicators(
    state: Optional[str] = Query(None, description="Filter by state"),
    city: Optional[str] = Query(None, description="Filter by city"),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """Get economic indicators by city/county"""
    query = db.query(EconomicIndicator)

    if state:
        query = query.filter(EconomicIndicator.state == state)
    if city:
        query = query.filter(EconomicIndicator.city == city)

    indicators = query.limit(limit).all()
    return [
        {
            "id": e.id,
            "city": e.city,
            "state": e.state,
            "county": e.county,
            "unemployment_rate": e.unemployment_rate,
            "employment_growth_rate": e.employment_growth_rate,
            "average_wage": e.average_wage,
            "median_wage": e.median_wage,
            "retail_sales_per_capita": e.retail_sales_per_capita,
            "business_establishments": e.business_establishments,
            "new_business_formations": e.new_business_formations,
            "gdp_per_capita": e.gdp_per_capita,
            "data_year": e.data_year,
            "source": e.source,
        }
        for e in indicators
    ]


@router.get("/development-projects", response_model=List[Dict])
def get_development_projects(
    state: Optional[str] = Query(None, description="Filter by state"),
    city: Optional[str] = Query(None, description="Filter by city"),
    project_type: Optional[str] = Query(None, description="Filter by project type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """Get development projects"""
    query = db.query(DevelopmentProject)

    if state:
        query = query.filter(DevelopmentProject.state == state)
    if city:
        query = query.filter(DevelopmentProject.city == city)
    if project_type:
        query = query.filter(DevelopmentProject.project_type == project_type)
    if status:
        query = query.filter(DevelopmentProject.status == status)

    projects = query.order_by(DevelopmentProject.start_date.desc()).limit(limit).all()
    return [
        {
            "id": p.id,
            "project_name": p.project_name,
            "address": p.address,
            "city": p.city,
            "state": p.state,
            "latitude": p.latitude,
            "longitude": p.longitude,
            "project_type": p.project_type,
            "square_feet": p.square_feet,
            "estimated_cost": p.estimated_cost,
            "start_date": p.start_date.isoformat() if p.start_date else None,
            "completion_date": (
                p.completion_date.isoformat() if p.completion_date else None
            ),
            "status": p.status,
            "developer_name": p.developer_name,
        }
        for p in projects
    ]
