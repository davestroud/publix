"""
Census API service for collecting demographic data

Uses US Census Bureau APIs:
- ACS 5-Year Estimates for demographics
- Population Estimates API for growth trends
- Geographic Areas API for metro definitions
"""

import os
import requests
import logging
from typing import Dict, Optional, List
from datetime import datetime
import time

logger = logging.getLogger(__name__)


class CensusService:
    """Service for fetching demographic data from US Census Bureau APIs"""

    def __init__(self):
        self.api_key = os.getenv("CENSUS_API_KEY")
        self.base_url = "https://api.census.gov/data"
        self.cache = {}  # Simple in-memory cache
        self.rate_limiter_delay = 0.1  # 100ms between requests (500/day limit)

    def _make_request(self, endpoint: str, params: Dict) -> Optional[Dict]:
        """Make API request with rate limiting and error handling"""
        # Census API: Key is optional for basic queries (500/day limit without key)
        # If key is provided, add it but don't fail if it's invalid
        # Some endpoints work without a key
        params_to_use = params.copy()
        if self.api_key:
            params_to_use["key"] = self.api_key.strip()  # Remove any whitespace

        # Check cache
        cache_key = f"{endpoint}:{str(params)}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        try:
            time.sleep(self.rate_limiter_delay)
            url = f"{self.base_url}/{endpoint}"

            # Try request with key if available
            response = None
            if self.api_key:
                params_with_key = params_to_use.copy()
                response = requests.get(url, params=params_with_key, timeout=10)

                # Check if we got "Invalid Key" HTML response
                if (
                    response.status_code == 200
                    and response.text
                    and "<html" in response.text.lower()
                ):
                    if (
                        "invalid key" in response.text.lower()
                        or "Invalid Key" in response.text
                    ):
                        logger.warning(
                            "Census API key appears invalid, trying without key..."
                        )
                        # Retry without key (works for basic queries up to 500/day)
                        params_with_key = params.copy()
                        response = requests.get(url, params=params_with_key, timeout=10)
            else:
                response = requests.get(url, params=params_to_use, timeout=10)

            # Log response for debugging
            logger.debug(f"Census API request: {url}")
            logger.debug(f"Response status: {response.status_code}")

            # Handle 204 No Content status (successful but no data)
            if response.status_code == 204:
                logger.warning(
                    f"Census API returned 204 No Content for {url} - data may not be available"
                )
                return None

            response.raise_for_status()

            # Check if response is empty
            if not response.text or len(response.text.strip()) == 0:
                logger.warning(f"Empty response from Census API: {url}")
                return None

            # Try to parse JSON
            try:
                data = response.json()
            except ValueError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                logger.error(f"Response text: {response.text[:500]}")
                # If it's HTML (error page), try without key
                if "<html" in response.text.lower() and self.api_key:
                    logger.info("Retrying Census API request without key...")
                    params_no_key = params.copy()
                    retry_response = requests.get(url, params=params_no_key, timeout=10)
                    if retry_response.status_code == 200 and retry_response.text:
                        try:
                            return retry_response.json()
                        except:
                            pass
                return None

            # Check for API errors in response
            if isinstance(data, dict) and "error" in data:
                error_msg = data.get("error", "Unknown error")
                logger.error(f"Census API error: {error_msg}")
                return None

            self.cache[cache_key] = data
            return data

        except requests.exceptions.HTTPError as e:
            logger.error(f"Census API HTTP error: {e}")
            if hasattr(e.response, "text"):
                logger.error(f"Response: {e.response.text[:500]}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Census API request failed: {e}")
            return None

    def get_city_demographics(self, city: str, state: str) -> Optional[Dict]:
        """
        Get demographics for a city using ACS 5-Year Estimates

        Args:
            city: City name
            state: State abbreviation (e.g., "FL")

        Returns:
            Dictionary with demographic data or None
        """
        # First, get the place FIPS code
        place_fips = self._get_place_fips(city, state)
        if not place_fips:
            logger.warning(f"Could not find FIPS code for {city}, {state}")
            return None

        # Get state FIPS code
        state_fips = self._get_state_fips(state)
        if not state_fips:
            logger.warning(f"Could not find state FIPS for {state}")
            return None

        # ACS 5-Year Estimates variables:
        # B01001_001E: Total population
        # B19013_001E: Median household income
        # B01002_001E: Median age
        # B25010_001E: Average household size
        params = {
            "get": "NAME,B01001_001E,B19013_001E,B01002_001E,B25010_001E",
            "for": f"place:{place_fips}",
            "in": f"state:{state_fips}",
        }

        data = self._make_request("2021/acs/acs5", params)
        if not data:
            logger.warning(f"No data returned from Census API for {city}, {state}")
            return None

        # Check if we got an error response
        if isinstance(data, dict) and "error" in data:
            error_msg = data.get("error", "Unknown error")
            logger.error(f"Census API error for {city}, {state}: {error_msg}")
            return None

        if len(data) < 2:
            logger.warning(f"Insufficient data returned for {city}, {state}: {data}")
            return None

        # Parse response (first row is headers, second is data)
        headers = data[0]
        values = data[1]

        result = {}
        for i, header in enumerate(headers):
            if i >= len(values):
                continue
            value = values[i]
            if header == "NAME":
                result["name"] = value
            elif header == "B01001_001E":
                try:
                    result["population"] = (
                        int(value) if value and value != "null" else None
                    )
                except (ValueError, TypeError):
                    result["population"] = None
            elif header == "B19013_001E":
                try:
                    result["median_income"] = (
                        float(value) if value and value != "null" else None
                    )
                except (ValueError, TypeError):
                    result["median_income"] = None
            elif header == "B01002_001E":
                try:
                    result["median_age"] = (
                        float(value) if value and value != "null" else None
                    )
                except (ValueError, TypeError):
                    result["median_age"] = None
            elif header == "B25010_001E":
                try:
                    result["household_size"] = (
                        float(value) if value and value != "null" else None
                    )
                except (ValueError, TypeError):
                    result["household_size"] = None

        # Determine data year from the endpoint used
        result["data_year"] = (
            2022  # Default to 2022, will be updated based on actual response
        )
        return result

    def get_population_growth(self, city: str, state: str) -> Optional[float]:
        """
        Calculate 5-year population growth rate

        Note: PEP API doesn't support place-level geography for all cities.
        Falls back to using ACS data comparison if PEP fails.

        Args:
            city: City name
            state: State abbreviation

        Returns:
            Annual growth rate (as decimal, e.g., 0.02 for 2%) or None
        """
        place_fips = self._get_place_fips(city, state)
        state_fips = self._get_state_fips(state)
        if not place_fips or not state_fips:
            return None

        # Try PEP API first (more accurate for growth)
        try:
            # Get current population (2022)
            current_params = {
                "get": "POP",
                "for": f"place:{place_fips}",
                "in": f"state:{state_fips}",
            }
            current_data = self._make_request("2022/pep/population", current_params)

            # Get population 5 years ago (2017)
            past_params = {
                "get": "POP",
                "for": f"place:{place_fips}",
                "in": f"state:{state_fips}",
            }
            past_data = self._make_request("2017/pep/population", past_params)

            if (
                current_data
                and past_data
                and len(current_data) >= 2
                and len(past_data) >= 2
            ):
                try:
                    current_pop = (
                        int(current_data[1][0]) if current_data[1][0] else None
                    )
                    past_pop = int(past_data[1][0]) if past_data[1][0] else None

                    if current_pop and past_pop and past_pop > 0:
                        # Calculate annualized growth rate
                        growth_rate = ((current_pop / past_pop) ** (1 / 5)) - 1
                        return growth_rate
                except (ValueError, IndexError):
                    pass
        except Exception as e:
            logger.debug(f"PEP API failed for {city}, {state}: {e}")

        # Fallback: Use ACS data comparison (less accurate but available)
        # Compare current ACS data with older ACS data
        try:
            current_demo = self.get_city_demographics(city, state)
            if current_demo and current_demo.get("population"):
                # Try to get older ACS data (2016 ACS 5-year)
                old_params = {
                    "get": "B01001_001E",  # Total population
                    "for": f"place:{place_fips}",
                    "in": f"state:{state_fips}",
                }
                old_data = self._make_request("2016/acs/acs5", old_params)

                if old_data and len(old_data) >= 2:
                    try:
                        old_pop = int(old_data[1][0]) if old_data[1][0] else None
                        current_pop = current_demo.get("population")

                        if old_pop and current_pop and old_pop > 0:
                            # Calculate annualized growth rate (6 year span for 2016-2022)
                            growth_rate = ((current_pop / old_pop) ** (1 / 6)) - 1
                            return growth_rate
                    except (ValueError, IndexError):
                        pass
        except Exception as e:
            logger.debug(f"ACS fallback failed for {city}, {state}: {e}")

        # If all methods fail, return None (growth rate will be missing)
        return None

    def get_metro_area(self, city: str, state: str) -> Optional[str]:
        """
        Get metro area (MSA/CBSA) code for a city

        Args:
            city: City name
            state: State abbreviation

        Returns:
            MSA code or None
        """
        # This is a simplified version - full implementation would use
        # Census Geographic Areas API or a lookup table
        # For now, return None and let it be populated manually or via LLM analysis
        return None

    def _get_state_fips(self, state: str) -> Optional[str]:
        """Get state FIPS code"""
        state_fips_map = {
            "AL": "01",
            "AK": "02",
            "AZ": "04",
            "AR": "05",
            "CA": "06",
            "CO": "08",
            "CT": "09",
            "DE": "10",
            "FL": "12",
            "GA": "13",
            "HI": "15",
            "ID": "16",
            "IL": "17",
            "IN": "18",
            "IA": "19",
            "KS": "20",
            "KY": "21",
            "LA": "22",
            "ME": "23",
            "MD": "24",
            "MA": "25",
            "MI": "26",
            "MN": "27",
            "MS": "28",
            "MO": "29",
            "MT": "30",
            "NE": "31",
            "NV": "32",
            "NH": "33",
            "NJ": "34",
            "NM": "35",
            "NY": "36",
            "NC": "37",
            "ND": "38",
            "OH": "39",
            "OK": "40",
            "OR": "41",
            "PA": "42",
            "RI": "43",
            "SC": "45",
            "SD": "46",
            "TN": "47",
            "TX": "48",
            "UT": "49",
            "VT": "50",
            "VA": "51",
            "WA": "53",
            "WV": "54",
            "WI": "55",
            "WY": "56",
            "DC": "11",
        }
        return state_fips_map.get(state.upper())

    def _get_fips_from_census_api(self, city: str, state: str) -> Optional[str]:
        """
        Get place FIPS code by querying Census API for all places in state
        This is more reliable than static lookup tables
        """
        try:
            state_fips = self._get_state_fips(state)
            if not state_fips:
                return None

            # Query Census API for all places in state and find matching city
            url = f"{self.base_url}/2022/acs/acs5"
            params = {
                "get": "NAME,PLACE",
                "for": "place:*",
                "in": f"state:{state_fips}",
            }
            if self.api_key:
                params["key"] = self.api_key.strip()

            time.sleep(self.rate_limiter_delay)
            response = requests.get(url, params=params, timeout=10)

            if response.status_code != 200 or not response.text:
                return None

            try:
                data = response.json()
                if not data or len(data) < 2:
                    return None

                # Search for city name in results
                city_lower = city.lower()
                for row in data[1:]:  # Skip header row
                    if len(row) >= 2:
                        place_name = row[0].lower()
                        place_fips = row[1]

                        # Check if city name matches (handle variations like "Lexington-Fayette")
                        if city_lower in place_name or place_name.startswith(
                            city_lower
                        ):
                            logger.debug(
                                f"Found FIPS {place_fips} for {city}, {state} via Census API"
                            )
                            return place_fips

            except (ValueError, IndexError) as e:
                logger.debug(f"Failed to parse Census API response: {e}")
                return None

        except Exception as e:
            logger.debug(f"Census API FIPS lookup failed for {city}, {state}: {e}")

        return None

    def _get_place_fips(self, city: str, state: str) -> Optional[str]:
        """
        Get place FIPS code for a city using Census API lookup or fallback table
        """
        # First try to get from Census API dynamically (most reliable)
        fips_from_api = self._get_fips_from_census_api(city, state)
        if fips_from_api:
            return fips_from_api

        # Fallback to lookup table
        city_fips_map = {
            # Florida
            ("Miami", "FL"): "1245000",
            ("Tampa", "FL"): "1271000",
            ("Orlando", "FL"): "1253000",
            ("Jacksonville", "FL"): "1235000",
            ("Lakeland", "FL"): "1238250",
            ("Kissimmee", "FL"): "1236975",
            ("Clearwater", "FL"): "1212875",
            ("St. Petersburg", "FL"): "1263000",
            ("Tallahassee", "FL"): "1270750",
            ("Gainesville", "FL"): "1225875",
            ("Pensacola", "FL"): "1255900",
            ("Sarasota", "FL"): "1264175",
            ("Naples", "FL"): "1247650",
            ("Fort Myers", "FL"): "1224175",
            ("West Palm Beach", "FL"): "1276675",
            # Kentucky
            ("Lexington", "KY"): "2146042",
            ("Louisville", "KY"): "2148000",
            ("Owensboro", "KY"): "2158624",
            ("Bowling Green", "KY"): "2108992",
            ("Covington", "KY"): "2117854",
            ("Hopkinsville", "KY"): "2137852",
            ("Richmond", "KY"): "2165202",
            ("Florence", "KY"): "2127982",
            ("Georgetown", "KY"): "2130700",
            ("Henderson", "KY"): "2135896",
            ("Elizabethtown", "KY"): "2124298",
            ("Paducah", "KY"): "2158836",
            ("Radcliff", "KY"): "2159364",
            ("Ashland", "KY"): "2102206",
            ("Madisonville", "KY"): "2149290",
            ("Somerset", "KY"): "2161446",
            ("Danville", "KY"): "2119890",
            ("Fort Thomas", "KY"): "2128580",
            ("Shively", "KY"): "2160306",
            ("Newport", "KY"): "2155830",
            ("St. Matthews", "KY"): "2160012",
            ("Walton", "KY"): "2180524",
            ("Erlanger", "KY"): "2125282",
            ("Jeffersontown", "KY"): "2139988",
            # Georgia
            ("Atlanta", "GA"): "1304000",
            ("Savannah", "GA"): "1369000",
            ("Augusta", "GA"): "1304000",
            ("Columbus", "GA"): "1319000",
            ("Athens", "GA"): "1303456",
            ("Sandy Springs", "GA"): "1368496",
            ("Roswell", "GA"): "1367000",
            ("Macon", "GA"): "1349000",
            ("Johns Creek", "GA"): "1342424",
            ("Albany", "GA"): "1301056",
            ("Warner Robins", "GA"): "1380704",
            ("Alpharetta", "GA"): "1301644",
            ("Marietta", "GA"): "1349796",
            ("Valdosta", "GA"): "1379000",
            ("Smyrna", "GA"): "1371600",
            # North Carolina
            ("Charlotte", "NC"): "3712000",
            ("Raleigh", "NC"): "3755000",
            ("Greensboro", "NC"): "3728000",
            ("Durham", "NC"): "3719000",
            ("Winston-Salem", "NC"): "3775000",
            ("Fayetteville", "NC"): "3722920",
            ("Cary", "NC"): "3710700",
            ("Wilmington", "NC"): "3774440",
            ("High Point", "NC"): "3731000",
            ("Asheville", "NC"): "3702140",
            # Tennessee
            ("Nashville", "TN"): "4752006",
            ("Knoxville", "TN"): "4740000",
            ("Memphis", "TN"): "4748000",
            ("Chattanooga", "TN"): "4714000",
            ("Clarksville", "TN"): "4715120",
            ("Murfreesboro", "TN"): "4751580",
            ("Franklin", "TN"): "4727740",
            ("Jackson", "TN"): "4737680",
            ("Johnson City", "TN"): "4738320",
            ("Bartlett", "TN"): "4703280",
            # Virginia
            ("Richmond", "VA"): "5170000",
            ("Virginia Beach", "VA"): "5181000",
            ("Norfolk", "VA"): "5157000",
            ("Chesapeake", "VA"): "5151000",
            ("Newport News", "VA"): "5156000",
            ("Alexandria", "VA"): "5151000",
            ("Hampton", "VA"): "5145248",
            ("Portsmouth", "VA"): "5164000",
            ("Suffolk", "VA"): "5176000",
            ("Roanoke", "VA"): "5168000",
            # South Carolina
            ("Charleston", "SC"): "4513300",
            ("Columbia", "SC"): "4516000",
            ("North Charleston", "SC"): "4550605",
            ("Mount Pleasant", "SC"): "4548570",
            ("Rock Hill", "SC"): "4546100",
            ("Greenville", "SC"): "4532085",
            ("Summerville", "SC"): "4541055",
            ("Sumter", "SC"): "4541055",
            ("Hilton Head Island", "SC"): "4534045",
            ("Spartanburg", "SC"): "4536820",
            # Alabama
            ("Birmingham", "AL"): "0107000",
            ("Mobile", "AL"): "0150000",
            ("Montgomery", "AL"): "0151000",
            ("Huntsville", "AL"): "0137000",
            ("Tuscaloosa", "AL"): "0156000",
            ("Hoover", "AL"): "0135856",
            ("Auburn", "AL"): "0103084",
            ("Dothan", "AL"): "0111204",
            ("Decatur", "AL"): "0110128",
            ("Madison", "AL"): "0145456",
        }

        key = (city.title(), state.upper())
        fips = city_fips_map.get(key)

        # If not in lookup table, try Census Geocoder API as final fallback
        if not fips:
            fips = self._get_fips_from_geocoder(city, state)
            if fips:
                logger.info(f"Found FIPS {fips} for {city}, {state} via geocoder")

        return fips

    def _get_fips_from_geocoder(self, city: str, state: str) -> Optional[str]:
        """
        Get FIPS code using Census Geocoder API (doesn't require API key)
        """
        try:
            geocoder_url = (
                "https://geocoding.geo.census.gov/geocoder/geographies/address"
            )
            params = {
                "street": "",
                "city": city,
                "state": state,
                "benchmark": "Public_AR_Current",
                "vintage": "Current_Current",
                "format": "json",
            }

            time.sleep(self.rate_limiter_delay)
            response = requests.get(geocoder_url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            if data.get("result") and data["result"].get("addressMatches"):
                match = data["result"]["addressMatches"][0]
                geographies = match.get("geographies", {})
                places = geographies.get("Places", [])
                if places:
                    place_fips = places[0].get("PLACE", "")
                    if place_fips:
                        logger.debug(
                            f"Found FIPS {place_fips} for {city}, {state} via geocoder"
                        )
                        return place_fips

        except Exception as e:
            logger.debug(f"Geocoder API failed for {city}, {state}: {e}")

        return None

    def get_comprehensive_demographics(self, city: str, state: str) -> Optional[Dict]:
        """
        Get comprehensive demographics including growth rate

        Args:
            city: City name
            state: State abbreviation

        Returns:
            Dictionary with all demographic data
        """
        demographics = self.get_city_demographics(city, state)
        if not demographics:
            return None

        # Add growth rate (skip if PEP API fails - it's not critical)
        try:
            growth_rate = self.get_population_growth(city, state)
            if growth_rate is not None:
                demographics["growth_rate"] = growth_rate
        except Exception as e:
            logger.debug(f"Could not calculate growth rate for {city}, {state}: {e}")
            # Growth rate is optional, continue without it

        # Add metro area (if available)
        metro_area = self.get_metro_area(city, state)
        if metro_area:
            demographics["metro_area"] = metro_area

        return demographics
