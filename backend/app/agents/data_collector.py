"""Data Collector Agent - Gathers store locations, demographics, and zoning data"""

from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.services.llm_service import call_llm, create_agent_prompt
from app.services.scraper import (
    PublixScraper,
    CompetitorScraper,
    ZoningScraper,
    DemographicsService,
)

from app.models.schemas import (
    PublixStore,
    CompetitorStore,
    Demographics,
    ZoningRecord,
    ShoppingCenter,
    TrafficData,
    NewsArticle,
    EconomicIndicator,
    DevelopmentProject,
)
from app.services.s3_service import get_s3_service

# from langsmith import traceable  # COMMENTED OUT: LangSmith causing 403 errors
import logging

logger = logging.getLogger(__name__)


# No-op decorator to replace @traceable
def traceable(name=None):
    def decorator(func_or_class):
        return func_or_class

    return decorator


# Try to use Google Places scraper if available
try:
    from app.services.scraper_google_places import (
        PublixScraperGooglePlaces,
        CompetitorScraperGooglePlaces,
    )
    import os
    from dotenv import load_dotenv

    load_dotenv()
    GOOGLE_PLACES_AVAILABLE = bool(os.getenv("GOOGLE_PLACES_API_KEY"))
except (ImportError, Exception) as e:
    GOOGLE_PLACES_AVAILABLE = False
    logger.debug(f"Google Places not available: {e}")


@traceable(name="data_collector_agent")
class DataCollectorAgent:
    """Agent responsible for collecting data from various sources"""

    def __init__(self, db: Session):
        self.db = db
        self.s3_service = get_s3_service()
        # Use Google Places scraper if available (more reliable)
        if GOOGLE_PLACES_AVAILABLE:
            try:
                self.publix_scraper = PublixScraperGooglePlaces()
                self.competitor_scraper = CompetitorScraperGooglePlaces()
                logger.info("Using Google Places API scrapers (recommended)")
            except Exception as e:
                logger.warning(
                    f"Google Places scraper failed: {e}. Falling back to direct scraping."
                )
                self.publix_scraper = PublixScraper()
                self.competitor_scraper = CompetitorScraper()
        else:
            self.publix_scraper = PublixScraper()
            self.competitor_scraper = CompetitorScraper()
        self.zoning_scraper = ZoningScraper()
        self.demographics_service = DemographicsService()

        # Initialize new services
        try:
            from app.services.shopping_center_service import ShoppingCenterService

            self.shopping_center_service = ShoppingCenterService()
        except Exception as e:
            logger.warning(f"Failed to initialize shopping center service: {e}")
            self.shopping_center_service = None

        try:
            from app.services.traffic_service import TrafficService

            self.traffic_service = TrafficService()
        except Exception as e:
            logger.warning(f"Failed to initialize traffic service: {e}")
            self.traffic_service = None

        try:
            from app.services.news_service import NewsService

            self.news_service = NewsService()
        except Exception as e:
            logger.warning(f"Failed to initialize news service: {e}")
            self.news_service = None

        try:
            from app.services.economic_service import EconomicService

            self.economic_service = EconomicService()
        except Exception as e:
            logger.warning(f"Failed to initialize economic service: {e}")
            self.economic_service = None

    def collect_publix_stores(self, state: str = None) -> List[Dict[str, Any]]:
        """Collect current Publix store locations"""
        logger.info(f"Collecting Publix stores for state: {state}")

        context = """You are analyzing Publix store locations. Your task is to help identify
        where stores are located and understand their distribution patterns."""

        task = f"Collect and analyze Publix store locations{' in ' + state if state else 'across all states'}"

        # Use LLM to guide data collection strategy
        prompt = create_agent_prompt(
            agent_name="Data Collector", context=context, task=task
        )

        strategy = call_llm(prompt)
        logger.info(f"Data collection strategy: {strategy[:200]}...")

        # Scrape actual data
        stores = self.publix_scraper.scrape_stores(state=state)

        # Upload to S3 first (before database operations)
        if stores:
            self.s3_service.upload_stores(stores, store_type="publix", state=state)
            logger.info(f"Uploaded {len(stores)} Publix stores to S3")

        # Store in database (handle duplicates gracefully)
        saved_count = 0
        for store_data in stores:
            try:
                # Check if store already exists
                existing = (
                    self.db.query(PublixStore)
                    .filter_by(store_number=store_data.get("store_number"))
                    .first()
                )
                if existing:
                    continue  # Skip duplicates

                store = PublixStore(**store_data)
                self.db.add(store)
                saved_count += 1
            except Exception as e:
                logger.warning(
                    f"Failed to add store {store_data.get('store_number')}: {e}"
                )
                continue

        try:
            self.db.commit()
            logger.info(f"Saved {saved_count} new Publix stores to database")
        except Exception as e:
            logger.error(f"Database commit failed: {e}")
            self.db.rollback()

        return stores

    def collect_competitor_stores(self, state: str = None) -> Dict[str, List[Dict]]:
        """Collect competitor store locations"""
        logger.info(f"Collecting competitor stores for state: {state}")

        competitors = {}

        # Collect Walmart stores
        walmart_stores = self.competitor_scraper.scrape_walmart_stores(state=state)

        # Collect Chick-fil-A stores (high priority for retail synergy)
        chickfila_stores = []
        if hasattr(self.competitor_scraper, "scrape_chickfila_stores"):
            chickfila_stores = self.competitor_scraper.scrape_chickfila_stores(
                state=state
            )

        # Upload to S3 first
        if walmart_stores:
            self.s3_service.upload_stores(
                walmart_stores, store_type="walmart", state=state
            )
            logger.info(f"Uploaded {len(walmart_stores)} Walmart stores to S3")

        # Collect Kroger stores
        kroger_stores = self.competitor_scraper.scrape_kroger_stores(state=state)

        # Collect Target stores
        target_stores = []
        if hasattr(self.competitor_scraper, "scrape_target_stores"):
            target_stores = self.competitor_scraper.scrape_target_stores(state=state)

        # Collect Costco stores
        costco_stores = []
        if hasattr(self.competitor_scraper, "scrape_costco_stores"):
            costco_stores = self.competitor_scraper.scrape_costco_stores(state=state)

        # Upload to S3 first
        if kroger_stores:
            self.s3_service.upload_stores(
                kroger_stores, store_type="kroger", state=state
            )
            logger.info(f"Uploaded {len(kroger_stores)} Kroger stores to S3")

        if chickfila_stores:
            self.s3_service.upload_stores(
                chickfila_stores, store_type="chickfila", state=state
            )
            logger.info(f"Uploaded {len(chickfila_stores)} Chick-fil-A stores to S3")

        if target_stores:
            self.s3_service.upload_stores(
                target_stores, store_type="target", state=state
            )
            logger.info(f"Uploaded {len(target_stores)} Target stores to S3")

        if costco_stores:
            self.s3_service.upload_stores(
                costco_stores, store_type="costco", state=state
            )
            logger.info(f"Uploaded {len(costco_stores)} Costco stores to S3")

        # Store in database (handle duplicates gracefully)
        saved_walmart = 0
        for store_data in walmart_stores:
            try:
                existing = (
                    self.db.query(CompetitorStore)
                    .filter_by(
                        competitor_name="Walmart",
                        address=store_data.get("address"),
                        city=store_data.get("city"),
                    )
                    .first()
                )
                if existing:
                    continue
                store = CompetitorStore(competitor_name="Walmart", **store_data)
                self.db.add(store)
                saved_walmart += 1
            except Exception as e:
                logger.warning(f"Failed to add Walmart store: {e}")
                continue

        saved_kroger = 0
        for store_data in kroger_stores:
            try:
                existing = (
                    self.db.query(CompetitorStore)
                    .filter_by(
                        competitor_name="Kroger",
                        address=store_data.get("address"),
                        city=store_data.get("city"),
                    )
                    .first()
                )
                if existing:
                    continue
                store = CompetitorStore(competitor_name="Kroger", **store_data)
                self.db.add(store)
                saved_kroger += 1
            except Exception as e:
                logger.warning(f"Failed to add Kroger store: {e}")
                continue

        # Save Chick-fil-A stores
        saved_chickfila = 0
        for store_data in chickfila_stores:
            try:
                existing = (
                    self.db.query(CompetitorStore)
                    .filter_by(
                        competitor_name="Chick-fil-A",
                        address=store_data.get("address"),
                        city=store_data.get("city"),
                    )
                    .first()
                )
                if existing:
                    continue
                store = CompetitorStore(competitor_name="Chick-fil-A", **store_data)
                self.db.add(store)
                saved_chickfila += 1
            except Exception as e:
                logger.warning(f"Failed to add Chick-fil-A store: {e}")
                continue

        # Save Target stores
        saved_target = 0
        for store_data in target_stores:
            try:
                existing = (
                    self.db.query(CompetitorStore)
                    .filter_by(
                        competitor_name="Target",
                        address=store_data.get("address"),
                        city=store_data.get("city"),
                    )
                    .first()
                )
                if existing:
                    continue
                store = CompetitorStore(competitor_name="Target", **store_data)
                self.db.add(store)
                saved_target += 1
            except Exception as e:
                logger.warning(f"Failed to add Target store: {e}")
                continue

        # Save Costco stores
        saved_costco = 0
        for store_data in costco_stores:
            try:
                existing = (
                    self.db.query(CompetitorStore)
                    .filter_by(
                        competitor_name="Costco",
                        address=store_data.get("address"),
                        city=store_data.get("city"),
                    )
                    .first()
                )
                if existing:
                    continue
                store = CompetitorStore(competitor_name="Costco", **store_data)
                self.db.add(store)
                saved_costco += 1
            except Exception as e:
                logger.warning(f"Failed to add Costco store: {e}")
                continue

        competitors["Walmart"] = walmart_stores
        competitors["Kroger"] = kroger_stores
        competitors["Chick-fil-A"] = chickfila_stores
        competitors["Target"] = target_stores
        competitors["Costco"] = costco_stores

        try:
            self.db.commit()
            logger.info(
                f"Saved {saved_walmart} new Walmart and {saved_kroger} new Kroger stores to database"
            )
        except Exception as e:
            logger.error(f"Database commit failed: {e}")
            self.db.rollback()

        return competitors

    def collect_demographics(self, cities: List[Dict[str, str]]) -> List[Dict]:
        """Collect demographic data for cities"""
        logger.info(f"Collecting demographics for {len(cities)} cities")

        demographics_list = []
        for city_info in cities:
            city = city_info.get("city")
            state = city_info.get("state")

            demo_data = self.demographics_service.get_demographics(city, state)
            if demo_data:
                # Remove 'name' field if present (not in Demographics model)
                demo_data_clean = {k: v for k, v in demo_data.items() if k != "name"}
                demo = Demographics(city=city, state=state, **demo_data_clean)
                self.db.add(demo)
                demographics_list.append(demo_data)

        self.db.commit()
        return demographics_list

    def collect_zoning_records(
        self,
        cities: List[Dict[str, str]],
        min_acreage: float = 15.0,
        max_acreage: float = 25.0,
    ) -> List[Dict]:
        """Collect zoning records for commercial parcels"""
        logger.info(f"Collecting zoning records for {len(cities)} cities")

        all_records = []
        for city_info in cities:
            city = city_info.get("city")
            state = city_info.get("state")

            records = self.zoning_scraper.scrape_zoning_records(
                city=city, state=state, min_acreage=min_acreage, max_acreage=max_acreage
            )

            for record_data in records:
                record = ZoningRecord(city=city, state=state, **record_data)
                self.db.add(record)
                all_records.append(record_data)

        try:
            self.db.commit()
            logger.info(f"Collected {len(all_records)} zoning records")
        except Exception as e:
            logger.error(f"Database commit failed: {e}")
            self.db.rollback()

        return all_records

    def collect_parcels(
        self,
        city: str,
        state: str,
        min_acreage: float = 15.0,
        max_acreage: float = 25.0,
    ) -> List[Dict]:
        """Collect parcel data for a city"""
        from app.models.schemas import Parcel
        from app.services.parcel_service import ParcelService
        from app.services.analytics_service import AnalyticsService

        logger.info(
            f"Collecting parcels for {city}, {state} ({min_acreage}-{max_acreage} acres)"
        )

        parcel_service = ParcelService(db=self.db)
        parcels = parcel_service.get_parcels_by_city(
            city=city, state=state, min_acreage=min_acreage, max_acreage=max_acreage
        )

        if not parcels:
            logger.warning(f"No parcels found for {city}, {state}")
            return []

        # Calculate proximity metrics for each parcel
        analytics = AnalyticsService(self.db)
        saved_count = 0

        for parcel_data in parcels:
            try:
                # Check if parcel already exists
                existing = (
                    self.db.query(Parcel)
                    .filter_by(parcel_id=parcel_data.get("parcel_id"))
                    .first()
                )
                if existing:
                    continue

                # Calculate proximity to anchors
                if parcel_data.get("latitude") and parcel_data.get("longitude"):
                    proximity = analytics.calculate_parcel_proximity_metrics(
                        parcel_data["latitude"], parcel_data["longitude"], state
                    )
                    parcel_data["proximity_to_anchors"] = proximity.get(
                        "nearest_competitors", {}
                    )
                    parcel_data["retail_synergy_score"] = proximity.get(
                        "retail_synergy", {}
                    ).get("synergy_score", 0.0)

                parcel = Parcel(**parcel_data)
                self.db.add(parcel)
                saved_count += 1

            except Exception as e:
                logger.warning(f"Failed to add parcel: {e}")
                continue

        try:
            self.db.commit()
            logger.info(f"Saved {saved_count} new parcels to database")
        except Exception as e:
            logger.error(f"Database commit failed: {e}")
            self.db.rollback()

        # Upload to S3
        if parcels:
            self.s3_service.upload_json(
                parcels,
                key=f"parcels_{city}_{state}",
                folder="scraped-data",
                metadata={"city": city, "state": state, "count": len(parcels)},
            )

        return parcels

    def collect_municipal_codes(self, city: str, state: str) -> List[Dict]:
        """Collect municipal zoning codes"""
        from app.models.schemas import ZoningCode, ImpactFee
        from app.services.municipal_code_service import MunicipalCodeService

        logger.info(f"Collecting municipal codes for {city}, {state}")

        code_service = MunicipalCodeService()

        # Extract zoning codes
        zoning_data = code_service.extract_zoning_code(city, state)
        saved_zoning = 0

        if zoning_data and zoning_data.get("zoning_districts"):
            for district in zoning_data["zoning_districts"]:
                try:
                    existing = (
                        self.db.query(ZoningCode)
                        .filter_by(
                            city=city, state=state, zone_code=district.get("zone_code")
                        )
                        .first()
                    )
                    if existing:
                        continue

                    zone = ZoningCode(city=city, state=state, **district)
                    self.db.add(zone)
                    saved_zoning += 1
                except Exception as e:
                    logger.warning(f"Failed to add zoning code: {e}")
                    continue

        # Extract impact fees
        fees = code_service.extract_impact_fees(city, state)
        saved_fees = 0

        for fee_data in fees:
            try:
                existing = (
                    self.db.query(ImpactFee)
                    .filter_by(
                        city=city,
                        state=state,
                        fee_type=fee_data.get("fee_type"),
                        use_type=fee_data.get("use_type"),
                    )
                    .first()
                )
                if existing:
                    continue

                fee = ImpactFee(city=city, state=state, **fee_data)
                self.db.add(fee)
                saved_fees += 1
            except Exception as e:
                logger.warning(f"Failed to add impact fee: {e}")
                continue

        try:
            self.db.commit()
            logger.info(
                f"Saved {saved_zoning} zoning codes and {saved_fees} impact fees for {city}, {state}"
            )
        except Exception as e:
            logger.error(f"Database commit failed: {e}")
            self.db.rollback()

        return {"zoning_codes": saved_zoning, "impact_fees": saved_fees}

    def collect_planning_commission_records(self, city: str, state: str) -> List[Dict]:
        """Collect planning commission meeting records"""
        from app.models.schemas import PlanningCommissionRecord
        from app.services.planning_commission_scraper import PlanningCommissionScraper

        logger.info(f"Collecting planning commission records for {city}, {state}")

        scraper = PlanningCommissionScraper()
        records = scraper.scrape_meeting_agendas(city, state)

        saved_count = 0
        for record_data in records:
            try:
                existing = (
                    self.db.query(PlanningCommissionRecord)
                    .filter_by(
                        city=city,
                        state=state,
                        meeting_date=record_data.get("meeting_date"),
                        agenda_item=record_data.get("agenda_item"),
                    )
                    .first()
                )
                if existing:
                    continue

                record = PlanningCommissionRecord(**record_data)
                self.db.add(record)
                saved_count += 1
            except Exception as e:
                logger.warning(f"Failed to add planning commission record: {e}")
                continue

        try:
            self.db.commit()
            logger.info(
                f"Saved {saved_count} planning commission records for {city}, {state}"
            )
        except Exception as e:
            logger.error(f"Database commit failed: {e}")
            self.db.rollback()

        return records

    def collect_shopping_centers(self, city: str, state: str) -> List[Dict]:
        """Collect shopping center data for a city"""
        if (
            not self.shopping_center_service
            or not self.shopping_center_service.available
        ):
            logger.warning("Shopping center service not available")
            return []

        logger.info(f"Collecting shopping centers for {city}, {state}")

        centers = self.shopping_center_service.find_shopping_centers(city, state)
        saved_count = 0

        for center_data in centers:
            try:
                # Check if center already exists
                existing = (
                    self.db.query(ShoppingCenter)
                    .filter_by(place_id=center_data.get("place_id"))
                    .first()
                )
                if existing:
                    continue

                # Find anchor tenants for this center
                if center_data.get("latitude") and center_data.get("longitude"):
                    anchors = self.shopping_center_service.find_anchor_tenants(
                        center_data["latitude"], center_data["longitude"]
                    )
                    center_data["anchor_tenants"] = [
                        a.get("brand") for a in anchors if a.get("brand")
                    ]

                    # Calculate co-tenancy score
                    co_tenancy = self.shopping_center_service.analyze_co_tenancy(
                        city, state, center_data["latitude"], center_data["longitude"]
                    )
                    center_data["co_tenancy_score"] = co_tenancy.get(
                        "co_tenancy_score", 0
                    )

                center = ShoppingCenter(**center_data)
                self.db.add(center)
                saved_count += 1
            except Exception as e:
                logger.warning(f"Failed to add shopping center: {e}")
                continue

        try:
            self.db.commit()
            logger.info(f"Saved {saved_count} new shopping centers to database")
        except Exception as e:
            logger.error(f"Database commit failed: {e}")
            self.db.rollback()

        return centers

    def collect_traffic_data(
        self,
        latitude: float,
        longitude: float,
        city: str,
        state: str,
        location_id: str = None,
    ) -> Dict:
        """Collect traffic data for a location"""
        if not self.traffic_service or not self.traffic_service.available:
            logger.warning("Traffic service not available")
            return {}

        logger.info(f"Collecting traffic data for {city}, {state}")

        traffic_data = self.traffic_service.get_traffic_data_for_location(
            latitude, longitude, city, state
        )

        # Store in database
        try:
            traffic_record = TrafficData(
                location_id=location_id or f"{latitude},{longitude}",
                location_type="store",
                latitude=latitude,
                longitude=longitude,
                city=city,
                state=state,
                average_daily_traffic=traffic_data.get("average_daily_traffic"),
                peak_hour_volume=traffic_data.get("peak_hour_volume"),
                traffic_growth_rate=traffic_data.get("traffic_growth_rate"),
                accessibility_score=traffic_data.get("accessibility_score"),
                source=traffic_data.get("source", "google_maps"),
            )
            self.db.add(traffic_record)
            self.db.commit()
            logger.info("Saved traffic data to database")
        except Exception as e:
            logger.warning(f"Failed to save traffic data: {e}")
            self.db.rollback()

        return traffic_data

    def collect_news_articles(
        self, city: str = None, state: str = None, days: int = 30
    ) -> Dict[str, List[Dict]]:
        """Collect news articles about Publix and competitors"""
        if not self.news_service or not self.news_service.available:
            logger.warning("News service not available")
            return {}

        logger.info(
            f"Collecting news articles for {city or 'all locations'}, {state or 'all states'}"
        )

        all_articles = {}

        # Collect Publix news
        publix_articles = self.news_service.search_publix_news(city, state, days)
        saved_publix = 0

        for article_data in publix_articles:
            try:
                existing = (
                    self.db.query(NewsArticle)
                    .filter_by(url=article_data.get("url"))
                    .first()
                )
                if existing:
                    continue

                article = NewsArticle(**article_data)
                self.db.add(article)
                saved_publix += 1
            except Exception as e:
                logger.warning(f"Failed to add news article: {e}")
                continue

        all_articles["publix"] = publix_articles

        # Collect competitor news
        competitors = ["Walmart", "Kroger", "Target", "Costco"]
        for competitor in competitors:
            comp_articles = self.news_service.search_competitor_news(
                competitor, city, state, days
            )
            saved_comp = 0

            for article_data in comp_articles:
                try:
                    existing = (
                        self.db.query(NewsArticle)
                        .filter_by(url=article_data.get("url"))
                        .first()
                    )
                    if existing:
                        continue

                    article = NewsArticle(**article_data)
                    self.db.add(article)
                    saved_comp += 1
                except Exception as e:
                    logger.warning(f"Failed to add competitor news article: {e}")
                    continue

            all_articles[competitor.lower()] = comp_articles

        try:
            self.db.commit()
            logger.info(
                f"Saved {saved_publix} Publix articles and competitor articles to database"
            )
        except Exception as e:
            logger.error(f"Database commit failed: {e}")
            self.db.rollback()

        return all_articles

    def collect_economic_indicators(
        self, city: str, state: str, county: str = None
    ) -> Dict:
        """Collect economic indicators for a city/county"""
        if not self.economic_service or not self.economic_service.available:
            logger.warning("Economic service not available")
            return {}

        logger.info(f"Collecting economic indicators for {city}, {state}")

        indicators = self.economic_service.get_economic_indicators(city, state, county)

        # Store in database
        try:
            # Check if already exists
            existing = (
                self.db.query(EconomicIndicator)
                .filter_by(city=city, state=state, county=county)
                .first()
            )

            if existing:
                # Update existing record
                for key, value in indicators.items():
                    if hasattr(existing, key) and value is not None:
                        setattr(existing, key, value)
                from datetime import datetime

                existing.updated_at = datetime.utcnow()
                logger.info(f"Updated economic indicators for {city}, {state}")
            else:
                # Create new record
                indicator = EconomicIndicator(**indicators)
                self.db.add(indicator)
                logger.info(f"Added economic indicators for {city}, {state}")

            self.db.commit()
        except Exception as e:
            logger.warning(f"Failed to save economic indicators: {e}")
            self.db.rollback()

        return indicators

    def execute_collection_plan(self, region: str) -> Dict[str, Any]:
        """Execute comprehensive data collection for a region"""
        logger.info(f"Executing data collection plan for region: {region}")

        # Use LLM to create collection plan
        context = """You are creating a data collection plan for analyzing Publix expansion opportunities.
        Consider what data is needed: current store locations, competitor presence, demographics, and zoning records."""

        task = f"Create a data collection plan for region: {region}. Identify key cities and data sources."

        prompt = create_agent_prompt(
            agent_name="Data Collector", context=context, task=task
        )

        plan = call_llm(prompt)
        logger.info(f"Collection plan: {plan[:300]}...")

        # Execute collection
        results = {
            "publix_stores": self.collect_publix_stores(state=region),
            "competitor_stores": self.collect_competitor_stores(state=region),
            "demographics": [],
            "zoning_records": [],
        }

        # Upload complete results to S3
        self.s3_service.upload_collection_results(results, region=region)
        logger.info(f"Uploaded collection results for {region} to S3")

        return results
