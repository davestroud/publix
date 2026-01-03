"""
Economic Indicator Service - Collects economic data from BLS, FRED, and Census APIs
"""

import os
import requests
import logging
from typing import List, Dict, Optional
import time
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class EconomicService:
    """Service for collecting economic indicators"""

    def __init__(self):
        self.bls_api_key = os.getenv("BLS_API_KEY")
        self.fred_api_key = os.getenv("FRED_API_KEY")
        self.census_api_key = os.getenv("CENSUS_API_KEY")

        # BLS API (free, no key required for basic usage)
        self.bls_url = "https://api.bls.gov/publicAPI/v2/timeseries/data"

        # FRED API
        self.fred_url = "https://api.stlouisfed.org/fred"

        # Census Business Patterns API
        self.census_business_url = "https://api.census.gov/data"

        self.available = True  # BLS is free, others optional
        logger.info("Economic service initialized")

    def get_economic_indicators(
        self, city: str, state: str, county: Optional[str] = None
    ) -> Dict:
        """
        Get comprehensive economic indicators for a city/county

        Args:
            city: City name
            state: State abbreviation
            county: Optional county name

        Returns:
            Dictionary with economic indicators
        """
        indicators = {
            "city": city,
            "state": state,
            "county": county,
        }

        # Get unemployment data (if county available)
        if county:
            unemployment = self._get_unemployment_rate(state, county)
            if unemployment:
                indicators["unemployment_rate"] = unemployment

        # Get employment data
        employment = self._get_employment_data(state, county)
        if employment:
            indicators.update(employment)

        # Get wage data
        wages = self._get_wage_data(state, county)
        if wages:
            indicators.update(wages)

        # Get retail sales data (from Census Business Patterns)
        retail = self._get_retail_data(city, state)
        if retail:
            indicators.update(retail)

        return indicators

    def _get_unemployment_rate(self, state: str, county: str) -> Optional[float]:
        """Get unemployment rate from BLS API"""
        try:
            # BLS requires specific series IDs - this is simplified
            # In production, you'd need to map counties to BLS series IDs
            # For now, return None (would need proper series ID mapping)
            logger.debug("Unemployment rate lookup requires BLS series ID mapping")
            return None
        except Exception as e:
            logger.debug(f"Error getting unemployment rate: {e}")
            return None

    def _get_employment_data(
        self, state: str, county: Optional[str] = None
    ) -> Optional[Dict]:
        """Get employment growth data"""
        try:
            # Simplified - would use BLS or FRED APIs with proper series IDs
            # For now, return placeholder structure
            return {
                "employment_growth_rate": None,  # Would calculate from time series
                "business_establishments": None,  # From Census Business Patterns
                "new_business_formations": None,  # From Census or state data
            }
        except Exception as e:
            logger.debug(f"Error getting employment data: {e}")
            return None

    def _get_wage_data(
        self, state: str, county: Optional[str] = None
    ) -> Optional[Dict]:
        """Get wage data from BLS"""
        try:
            # Simplified - would use BLS Occupational Employment Statistics
            # For now, return placeholder structure
            return {
                "average_wage": None,  # Would get from BLS OES
                "median_wage": None,  # Would get from BLS OES
            }
        except Exception as e:
            logger.debug(f"Error getting wage data: {e}")
            return None

    def _get_retail_data(self, city: str, state: str) -> Optional[Dict]:
        """Get retail sales data from Census Business Patterns"""
        if not self.census_api_key:
            return None

        try:
            # Census Business Patterns API
            # Would need proper geography codes (FIPS)
            # This is a placeholder structure
            return {
                "retail_sales_per_capita": None,  # Would calculate from Census BP data
            }
        except Exception as e:
            logger.debug(f"Error getting retail data: {e}")
            return None

    def get_county_economic_data(self, county: str, state: str) -> Dict:
        """
        Get economic data for a county
        Uses FRED API for county-level data

        Args:
            county: County name
            state: State abbreviation

        Returns:
            Dictionary with county economic data
        """
        if not self.fred_api_key:
            logger.warning("FRED_API_KEY not set. County data unavailable.")
            return {}

        # Would use FRED API with proper county FIPS codes
        # This is a placeholder
        return {
            "county": county,
            "state": state,
            "gdp_per_capita": None,  # Would get from FRED
            "unemployment_rate": None,  # Would get from FRED
        }
