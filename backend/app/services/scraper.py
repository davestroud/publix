"""Web scraping service for Publix locations, competitors, and zoning data"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import time
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class RateLimiter:
    """Simple rate limiter for web scraping"""

    def __init__(self, min_delay: float = 1.0):
        self.min_delay = min_delay
        self.last_request_time = 0.0

    def wait(self):
        """Wait if necessary to respect rate limit"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_delay:
            time.sleep(self.min_delay - time_since_last)
        self.last_request_time = time.time()


rate_limiter = RateLimiter(min_delay=1.0)


class PublixScraper:
    """Scraper for Publix store locations"""

    def __init__(self):
        self.base_url = "https://www.publix.com"
        self.rate_limiter = RateLimiter(min_delay=2.0)
        self._direct_scraper = None

    def _get_direct_scraper(self):
        """Lazy load the direct scraper"""
        if self._direct_scraper is None:
            # Try simple scraper first (no browser needed - fastest)
            try:
                from app.services.publix_scraper_simple import PublixScraperSimple

                self._direct_scraper = PublixScraperSimple()
                logger.info(
                    "Using simple scraper (requests/BeautifulSoup - no browser needed)"
                )
            except ImportError:
                # Try improved Playwright scraper first (better parsing)
                try:
                    from app.services.publix_scraper_improved import (
                        PublixScraperImproved,
                    )

                    self._direct_scraper = PublixScraperImproved(headless=True)
                    logger.info(
                        "Using improved Playwright scraper (multiple extraction strategies)"
                    )
                except ImportError:
                    # Fall back to standard Playwright
                    try:
                        from app.services.publix_scraper_playwright import (
                            PublixScraperPlaywright,
                        )

                        self._direct_scraper = PublixScraperPlaywright(headless=True)
                        logger.info("Using Playwright scraper (recommended for macOS)")
                    except ImportError:
                        # Fall back to Selenium only if Playwright not available
                        try:
                            from app.services.publix_scraper import PublixScraperDirect

                            self._direct_scraper = PublixScraperDirect(headless=True)
                            logger.warning(
                                "Using Selenium scraper (not recommended on macOS)"
                            )
                        except ImportError:
                            logger.warning(
                                "No browser scraper available. Install playwright: poetry add playwright && poetry run playwright install"
                            )
                            return None
        return self._direct_scraper

    def scrape_stores(self, state: Optional[str] = None) -> List[Dict]:
        """
        Scrape Publix store locations directly from their website

        Uses Selenium to interact with Publix's store locator and extract data.
        Falls back to empty list if Selenium is not available.
        """
        logger.info(f"Scraping Publix stores for state: {state}")

        # Try direct scraping first
        direct_scraper = self._get_direct_scraper()
        if direct_scraper:
            try:
                stores = direct_scraper.scrape_stores(state=state)
                if stores:
                    logger.info(
                        f"Successfully scraped {len(stores)} stores using direct scraper"
                    )
                    return stores
            except Exception as e:
                logger.warning(
                    f"Direct scraping failed: {e}. Trying alternative methods..."
                )

        # Fallback: Try API endpoint if available (if Publix exposes one)
        # This would require reverse engineering their store locator API
        logger.warning("Direct scraping not available or failed. Returning empty list.")
        logger.info(
            "To enable scraping, install Playwright: poetry add playwright && poetry run playwright install"
        )
        return []


class CompetitorScraper:
    """Scraper for competitor store locations"""

    def __init__(self):
        self.rate_limiter = RateLimiter(min_delay=2.0)

    def scrape_walmart_stores(self, state: Optional[str] = None) -> List[Dict]:
        """Scrape Walmart store locations"""
        stores = []
        logger.info(f"Scraping Walmart stores for state: {state}")
        # TODO: Implement actual scraping logic
        return stores

    def scrape_kroger_stores(self, state: Optional[str] = None) -> List[Dict]:
        """Scrape Kroger store locations"""
        stores = []
        logger.info(f"Scraping Kroger stores for state: {state}")
        # TODO: Implement actual scraping logic
        return stores


class ZoningScraper:
    """Scraper for zoning and permitting records using Smarty API"""

    def __init__(self):
        self.rate_limiter = RateLimiter(min_delay=3.0)
        # Try to initialize Smarty service
        try:
            from app.services.smarty_service import SmartyService

            self.smarty_service = SmartyService()
            if self.smarty_service.available:
                logger.info("Using Smarty API for zoning records")
            else:
                logger.warning("Smarty API credentials not configured")
                self.smarty_service = None
        except Exception as e:
            logger.warning(f"Failed to initialize Smarty service: {e}")
            self.smarty_service = None

    def scrape_zoning_records(
        self,
        city: str,
        state: str,
        min_acreage: float = 15.0,
        max_acreage: float = 25.0,
    ) -> List[Dict]:
        """Scrape zoning records for commercial parcels using Smarty API"""
        records = []
        logger.info(f"Scraping zoning records for {city}, {state} using Smarty API")

        if not self.smarty_service or not self.smarty_service.available:
            logger.warning("Smarty API not available - skipping zoning records")
            return records

        try:
            # Use Smarty to search for parcels in the city
            parcels = self.smarty_service.search_parcels_by_city(
                city=city,
                state=state,
                min_acreage=min_acreage,
                max_acreage=max_acreage,
                property_type="commercial",
            )

            # Convert Smarty parcel data to zoning record format
            for parcel in parcels:
                record = {
                    "parcel_id": parcel.get("parcel_id"),
                    "address": parcel.get("address"),
                    "city": city,
                    "state": state,
                    "latitude": parcel.get("latitude"),
                    "longitude": parcel.get("longitude"),
                    "acreage": parcel.get("acreage"),
                    "zoning_status": parcel.get("zoning_status", "unknown"),
                    "permit_type": "commercial",
                    "description": parcel.get("description"),
                    "source_url": parcel.get("source_url"),
                    "additional_data": parcel.get("property_data", {}),
                }
                records.append(record)

            logger.info(f"Found {len(records)} zoning records via Smarty API")
        except Exception as e:
            logger.error(
                f"Error scraping zoning records with Smarty: {e}", exc_info=True
            )

        return records


class DemographicsService:
    """Service to fetch demographic data"""

    def __init__(self):
        try:
            from app.services.census_service import CensusService

            self.census_service = CensusService()
            logger.info("Census service initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize Census service: {e}")
            self.census_service = None

    def get_demographics(self, city: str, state: str) -> Optional[Dict]:
        """Fetch demographic data from Census API or other sources"""
        logger.info(f"Fetching demographics for {city}, {state}")

        if not self.census_service:
            logger.warning("Census service not available")
            return None

        try:
            demographics = self.census_service.get_comprehensive_demographics(
                city, state
            )
            if demographics:
                logger.info(
                    f"Retrieved demographics for {city}, {state}: population={demographics.get('population')}"
                )
            return demographics
        except Exception as e:
            logger.error(f"Error fetching demographics: {e}", exc_info=True)
            return None
