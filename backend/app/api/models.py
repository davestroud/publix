"""Pydantic models for API requests and responses"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class StoreResponse(BaseModel):
    """Publix store response model"""

    id: int
    store_number: Optional[str]
    address: str
    city: str
    state: str
    zip_code: Optional[str]
    latitude: float
    longitude: float
    square_feet: Optional[int]
    opening_date: Optional[datetime]

    class Config:
        from_attributes = True


class PredictionResponse(BaseModel):
    """Prediction response model"""

    id: int
    city: str
    state: str
    latitude: Optional[float]
    longitude: Optional[float]
    confidence_score: float
    reasoning: str
    predicted_store_size: Optional[int]
    key_factors: Optional[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True


class AnalysisRequest(BaseModel):
    """Request model for triggering analysis"""

    region: str = Field(..., description="State or region to analyze")
    cities: Optional[List[Dict[str, str]]] = Field(
        None, description="Optional list of specific cities to evaluate"
    )


class AnalysisResponse(BaseModel):
    """Response model for analysis results"""

    analysis_run_id: int
    status: str
    predictions: List[PredictionResponse]
    report: Dict[str, Any]
    analysis_data: Dict[str, Any]


class CityAnalysisRequest(BaseModel):
    """Request model for single city analysis"""

    city: str
    state: str


class DemographicsResponse(BaseModel):
    """Demographics response model"""

    id: int
    city: str
    state: str
    population: Optional[int]
    median_income: Optional[float]
    growth_rate: Optional[float]
    median_age: Optional[float]
    household_size: Optional[float]
    data_year: Optional[int]

    class Config:
        from_attributes = True


class ZoningRecordResponse(BaseModel):
    """Zoning record response model"""

    id: int
    parcel_id: Optional[str]
    address: Optional[str]
    city: str
    state: str
    latitude: Optional[float]
    longitude: Optional[float]
    acreage: Optional[float]
    zoning_status: Optional[str]
    permit_type: Optional[str]
    description: Optional[str]
    record_date: Optional[datetime]

    class Config:
        from_attributes = True


class DashboardStatsResponse(BaseModel):
    """Dashboard statistics response"""

    total_stores: int
    total_predictions: int
    average_confidence: float
    recent_predictions: List[PredictionResponse]
    total_competitors: Optional[int] = 0
    total_demographics: Optional[int] = 0
    total_parcels: Optional[int] = 0
    total_zoning_records: Optional[int] = 0
    stores_by_state: Optional[Dict[str, int]] = {}
    competitors_by_type: Optional[Dict[str, int]] = {}
    demographics_by_state: Optional[Dict[str, int]] = {}
    parcels_by_state: Optional[Dict[str, int]] = {}


class ChatRequest(BaseModel):
    """Chat request model"""

    message: str = Field(..., description="User message")
    conversation_history: Optional[List[Dict[str, str]]] = Field(
        None, description="Previous conversation messages"
    )


class ChatResponse(BaseModel):
    """Chat response model"""

    response: str
    model: Optional[str] = None
    data: Optional[List[Dict]] = None
    query_type: Optional[str] = None
    error: Optional[bool] = False
