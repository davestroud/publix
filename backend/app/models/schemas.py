"""SQLAlchemy database models"""

from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Text,
    Boolean,
    ForeignKey,
    JSON,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class PublixStore(Base):
    """Current Publix store locations"""

    __tablename__ = "publix_stores"

    id = Column(Integer, primary_key=True, index=True)
    store_number = Column(String, unique=True, index=True)
    address = Column(String, nullable=False)
    city = Column(String, nullable=False, index=True)
    state = Column(String, nullable=False, index=True)
    zip_code = Column(String)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    square_feet = Column(Integer)
    opening_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CompetitorStore(Base):
    """Competitor store locations (Walmart, Kroger, etc.)"""

    __tablename__ = "competitor_stores"

    id = Column(Integer, primary_key=True, index=True)
    competitor_name = Column(
        String, nullable=False, index=True
    )  # Walmart, Kroger, etc.
    address = Column(String, nullable=False)
    city = Column(String, nullable=False, index=True)
    state = Column(String, nullable=False, index=True)
    zip_code = Column(String)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    square_feet = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Demographics(Base):
    """City/region demographic data"""

    __tablename__ = "demographics"

    id = Column(Integer, primary_key=True, index=True)
    city = Column(String, nullable=False, index=True)
    state = Column(String, nullable=False, index=True)
    population = Column(Integer)
    population_5yr_ago = Column(Integer)  # For growth calculation
    median_income = Column(Float)
    growth_rate = Column(Float)  # Annual population growth rate
    median_age = Column(Float)
    household_size = Column(Float)
    metro_area = Column(String)  # MSA/CBSA code
    stores_per_capita = Column(Float)  # Calculated: stores per 100K population
    data_year = Column(Integer)
    additional_data = Column(
        JSON
    )  # Additional demographic data (saturation scores, etc.)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Parcel(Base):
    """Parcel/land data for site identification"""

    __tablename__ = "parcels"

    id = Column(Integer, primary_key=True, index=True)
    parcel_id = Column(String, unique=True, index=True)  # APN/PIN
    address = Column(String)
    city = Column(String, nullable=False, index=True)
    state = Column(String, nullable=False, index=True)
    acreage = Column(Float, index=True)  # Filter 15-25 acres
    current_zoning = Column(String)
    owner_name = Column(String)
    owner_type = Column(String)  # individual, LLC, corporation
    assessed_value = Column(Float)
    land_use_code = Column(String)
    latitude = Column(Float, index=True)
    longitude = Column(Float, index=True)
    boundary_geojson = Column(JSON)  # Polygon coordinates
    existing_uses = Column(JSON)  # List of current businesses
    assemblage_score = Column(Float)  # Lower = easier to buy out
    proximity_to_anchors = Column(JSON)  # Distances to Walmart, Kroger, etc.
    retail_synergy_score = Column(Float)  # Number of anchors within 2 miles
    additional_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ZoningRecord(Base):
    """Zoning/permitting records"""

    __tablename__ = "zoning_records"

    id = Column(Integer, primary_key=True, index=True)
    parcel_id = Column(String, index=True)
    address = Column(String)
    city = Column(String, nullable=False, index=True)
    state = Column(String, nullable=False, index=True)
    latitude = Column(Float)
    longitude = Column(Float)
    acreage = Column(Float)  # Parcel size in acres
    zoning_status = Column(String)  # pending, approved, denied
    permit_type = Column(String)  # commercial, rezoning, etc.
    description = Column(Text)  # Project description
    record_date = Column(DateTime)
    source_url = Column(String)
    planning_commission_record_id = Column(
        Integer, ForeignKey("planning_commission_records.id")
    )
    additional_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Prediction(Base):
    """Generated predictions for new store locations"""

    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    city = Column(String, nullable=False, index=True)
    state = Column(String, nullable=False, index=True)
    latitude = Column(Float)
    longitude = Column(Float)
    confidence_score = Column(Float, nullable=False)  # 0.0 to 1.0
    reasoning = Column(Text, nullable=False)  # LLM-generated reasoning
    predicted_store_size = Column(Integer)  # Square feet
    key_factors = Column(JSON)  # List of key factors
    analysis_run_id = Column(Integer, ForeignKey("analysis_runs.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    analysis_run = relationship("AnalysisRun", back_populates="predictions")


class ZoningCode(Base):
    """Municipal zoning code data"""

    __tablename__ = "zoning_codes"

    id = Column(Integer, primary_key=True, index=True)
    city = Column(String, nullable=False, index=True)
    state = Column(String, nullable=False, index=True)
    zone_code = Column(String)  # e.g., "C-2", "Commercial"
    zone_name = Column(String)
    permitted_uses = Column(JSON)  # List of allowed uses
    setback_front = Column(Float)  # feet
    setback_side = Column(Float)
    setback_rear = Column(Float)
    parking_spaces_per_1000sqft = Column(Float)
    max_coverage = Column(Float)  # percentage
    max_height = Column(Float)  # feet
    source_url = Column(String)
    raw_text = Column(Text)  # Original code text
    additional_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ImpactFee(Base):
    """Impact fee schedules by municipality"""

    __tablename__ = "impact_fees"

    id = Column(Integer, primary_key=True, index=True)
    city = Column(String, nullable=False, index=True)
    state = Column(String, nullable=False, index=True)
    fee_type = Column(String)  # utility, traffic, school, etc.
    use_type = Column(String)  # commercial, retail, grocery, etc.
    fee_per_sqft = Column(Float)
    fee_methodology = Column(Text)  # How fee is calculated
    source_url = Column(String)
    effective_date = Column(DateTime)
    additional_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PlanningCommissionRecord(Base):
    """Planning commission meeting records"""

    __tablename__ = "planning_commission_records"

    id = Column(Integer, primary_key=True, index=True)
    city = Column(String, nullable=False, index=True)
    state = Column(String, nullable=False, index=True)
    meeting_date = Column(DateTime, index=True)
    agenda_item = Column(String)
    project_description = Column(Text)
    parcel_address = Column(String)
    application_status = Column(String)  # pending, approved, denied
    project_type = Column(String)  # grocery, commercial, rezoning, etc.
    square_feet = Column(Integer)  # If mentioned
    source_url = Column(String)
    raw_text = Column(Text)  # Original meeting minutes/agenda
    additional_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AnalysisRun(Base):
    """Track analysis execution history"""

    __tablename__ = "analysis_runs"

    id = Column(Integer, primary_key=True, index=True)
    region = Column(String)  # State or region analyzed
    status = Column(String, default="pending")  # pending, running, completed, failed
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    error_message = Column(Text)
    additional_data = Column(JSON)

    predictions = relationship("Prediction", back_populates="analysis_run")


class ShoppingCenter(Base):
    """Shopping centers and malls"""

    __tablename__ = "shopping_centers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String)
    city = Column(String, nullable=False, index=True)
    state = Column(String, nullable=False, index=True)
    zip_code = Column(String)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    place_id = Column(String, unique=True, index=True)  # Google Places ID
    rating = Column(Float)
    user_rating_count = Column(Integer)
    square_feet = Column(Integer)  # Estimated or actual
    occupancy_rate = Column(Float)  # 0.0 to 1.0
    anchor_tenants = Column(JSON)  # List of anchor tenant names
    co_tenancy_score = Column(Float)  # Calculated score
    additional_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TrafficData(Base):
    """Traffic volume data"""

    __tablename__ = "traffic_data"

    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(String, index=True)  # Reference to store/parcel
    location_type = Column(String)  # store, parcel, intersection
    road_name = Column(String)
    city = Column(String, index=True)
    state = Column(String, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    average_daily_traffic = Column(Integer)  # ADT
    peak_hour_volume = Column(Integer)
    traffic_growth_rate = Column(Float)  # Annual growth
    accessibility_score = Column(Float)  # 0.0 to 1.0
    data_year = Column(Integer)
    source = Column(String)  # API source
    additional_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class NewsArticle(Base):
    """News articles about Publix/competitors"""

    __tablename__ = "news_articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text)
    source = Column(String)  # News source name
    url = Column(String, unique=True, index=True)
    published_date = Column(DateTime, index=True)
    city = Column(String, index=True)
    state = Column(String, index=True)
    topic = Column(String)  # expansion, opening, closure, etc.
    sentiment = Column(String)  # positive, negative, neutral
    mentions_publix = Column(Boolean, default=False)
    mentions_competitor = Column(String)  # Competitor name if mentioned
    relevance_score = Column(Float)  # 0.0 to 1.0
    additional_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class EconomicIndicator(Base):
    """Economic indicators by city/county"""

    __tablename__ = "economic_indicators"

    id = Column(Integer, primary_key=True, index=True)
    city = Column(String, nullable=False, index=True)
    state = Column(String, nullable=False, index=True)
    county = Column(String, index=True)
    unemployment_rate = Column(Float)
    employment_growth_rate = Column(Float)  # Annual growth
    average_wage = Column(Float)
    median_wage = Column(Float)
    retail_sales_per_capita = Column(Float)
    business_establishments = Column(Integer)
    new_business_formations = Column(Integer)
    gdp_per_capita = Column(Float)
    data_year = Column(Integer)
    source = Column(String)  # BLS, FRED, Census, etc.
    additional_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DevelopmentProject(Base):
    """New development projects"""

    __tablename__ = "development_projects"

    id = Column(Integer, primary_key=True, index=True)
    project_name = Column(String)
    address = Column(String)
    city = Column(String, nullable=False, index=True)
    state = Column(String, nullable=False, index=True)
    latitude = Column(Float)
    longitude = Column(Float)
    project_type = Column(String)  # residential, commercial, mixed-use
    square_feet = Column(Integer)
    estimated_cost = Column(Float)
    start_date = Column(DateTime)
    completion_date = Column(DateTime)
    status = Column(String)  # planned, under_construction, completed
    developer_name = Column(String)
    source_url = Column(String)
    additional_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
