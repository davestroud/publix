"""
Example implementation using Google Places API (New) for store locations

To use this:
1. Get Google Places API key: https://console.cloud.google.com/
2. Enable "Places API (New)" in Google Cloud Console
3. Add to .env: GOOGLE_PLACES_API_KEY=your_key
4. Install: poetry add googlemaps
5. Replace scraper imports in data_collector.py

Note: Uses the NEW Places API, not the legacy one.
"""

import os
from typing import List, Dict, Optional
import logging
import requests

logger = logging.getLogger(__name__)

try:
    import googlemaps

    GOOGLEMAPS_AVAILABLE = True
except ImportError:
    GOOGLEMAPS_AVAILABLE = False
    logger.warning("googlemaps not installed. Install with: poetry add googlemaps")


class PublixScraperGooglePlaces:
    """Scraper for Publix stores using Google Places API (New)"""

    def __init__(self):
        self.api_key = os.getenv("GOOGLE_PLACES_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_PLACES_API_KEY not set in environment")

        # Use the new Places API endpoint
        self.base_url = "https://places.googleapis.com/v1/places:searchText"

    def scrape_stores(self, state: Optional[str] = None) -> List[Dict]:
        """
        Scrape Publix stores using Google Places API (New)

        For states with many stores (like FL with ~899), searches by major cities
        to bypass Google Places API result limits.
        """
        stores = []
        seen_store_ids = set()  # Track duplicates

        # For large states, use multiple strategies to get all stores
        if state and state in ["FL", "GA"]:
            major_cities = self._get_major_cities_for_state(state)
            logger.info(
                f"Searching {len(major_cities)} major cities in {state} with multiple query strategies"
            )

            # Strategy 1: Search by city with multiple query variations
            query_variations = [
                "Publix",  # Generic
                "Publix grocery",  # Grocery stores
                "Publix supermarket",  # Supermarkets
                "Publix pharmacy",  # Pharmacies
            ]

            for city in major_cities:
                for query_type in query_variations:
                    query = f"{query_type} in {city}, {state}"
                    city_stores = self._search_stores(query, state, seen_store_ids)
                    stores.extend(city_stores)
                    if city_stores:
                        logger.debug(
                            f"Found {len(city_stores)} stores in {city}, {state} (query: {query_type})"
                        )
        else:
            # For smaller states, search state-wide with multiple queries
            query_variations = ["Publix", "Publix grocery", "Publix supermarket"]
            for query_type in query_variations:
                query = query_type
                if state:
                    query += f" in {state}"
                logger.info(f"Searching Google Places API (New) for: {query}")
                state_stores = self._search_stores(query, state, seen_store_ids)
                stores.extend(state_stores)

        logger.info(
            f"Found {len(stores)} total Publix stores for {state} via Google Places API"
        )

        # Strategy 2: Fallback to direct Publix website scraping if we got fewer stores than expected
        expected_counts = {
            "FL": 899,
            "GA": 220,
            "AL": 96,
            "SC": 70,
            "TN": 59,
            "NC": 58,
            "VA": 24,
            "KY": 4,
        }
        expected = expected_counts.get(state, 0)

        if (
            expected > 0 and len(stores) < expected * 0.5
        ):  # If we got less than 50% of expected
            logger.info(
                f"Only found {len(stores)}/{expected} stores. Trying direct Publix website scraper as fallback..."
            )
            try:
                from app.services.publix_scraper_simple import PublixScraperSimple

                direct_scraper = PublixScraperSimple()
                direct_stores = direct_scraper.scrape_stores(state=state)

                # Merge with Google Places results, avoiding duplicates
                for store in direct_stores:
                    store_id = store.get("store_number") or store.get("address", "")
                    if store_id and store_id not in seen_store_ids:
                        stores.append(store)
                        seen_store_ids.add(store_id)

                logger.info(
                    f"Added {len(direct_stores)} stores from direct scraper. Total: {len(stores)}"
                )
            except Exception as e:
                logger.warning(f"Direct scraper fallback failed: {e}")

        logger.info(f"Final count: {len(stores)} Publix stores for {state}")
        return stores

    def _get_major_cities_for_state(self, state: str) -> List[str]:
        """Get major cities for a state to search individually"""
        major_cities_map = {
            "FL": [
                # Major metros
                "Miami",
                "Tampa",
                "Orlando",
                "Jacksonville",
                "Tallahassee",
                "Fort Lauderdale",
                "Pensacola",
                "Sarasota",
                "Naples",
                "West Palm Beach",
                "Clearwater",
                "St. Petersburg",
                "Gainesville",
                "Lakeland",
                "Kissimmee",
                # South Florida
                "Coral Springs",
                "Port St. Lucie",
                "Cape Coral",
                "Fort Myers",
                "Hollywood",
                "Pembroke Pines",
                "Miramar",
                "Hialeah",
                "Plantation",
                "Sunrise",
                "Boca Raton",
                "Deltona",
                "Palm Bay",
                "Largo",
                "Boynton Beach",
                "Davie",
                "Melbourne",
                "Pompano Beach",
                "Ocala",
                "Bradenton",
                "Fort Pierce",
                "Winter Haven",
                "Aventura",
                "Panama City",
                "Homestead",
                "Margate",
                "Winter Springs",
                "Altamonte Springs",
                "Sanford",
                "Casselberry",
                "Oviedo",
                "Lake Mary",
                "Apopka",
                "Winter Park",
                "Cocoa",
                "Rockledge",
                "Merritt Island",
                "Vero Beach",
                "Sebastian",
                "Stuart",
                "Jupiter",
                "Wellington",
                "Royal Palm Beach",
                "Lake Worth",
                "Deerfield Beach",
                "Coconut Creek",
                "Coral Gables",
                "Doral",
                "Kendall",
                "Cutler Bay",
                "Palmetto Bay",
                "North Miami",
                "Miami Beach",
                "South Miami",
                "Key Biscayne",
                "Weston",
                "Cooper City",
                # Additional cities
                "Titusville",
                "Palm Coast",
                "Port Orange",
                "Daytona Beach",
                "New Smyrna Beach",
                "Ormond Beach",
                "Deland",
                "Leesburg",
                "Mount Dora",
                "Eustis",
                "Tavares",
                "Clermont",
                "Windermere",
                "Celebration",
                "Davenport",
                "Haines City",
                "Winter Garden",
                "Groveland",
                "Mascotte",
                "Minneola",
                "Montverde",
                "Oakland",
                "Howey-in-the-Hills",
                "Lady Lake",
                "The Villages",
                "Belleview",
                "Dunnellon",
                "Crystal River",
                "Inverness",
                "Beverly Hills",
                "Lecanto",
                "Homosassa",
                "Spring Hill",
                "Brooksville",
                "Weeki Wachee",
                "New Port Richey",
                "Port Richey",
                "Hudson",
                "Tarpon Springs",
                "Dunedin",
                "Safety Harbor",
                "Oldsmar",
                "Palm Harbor",
                "Holiday",
                "Trinity",
                "Odessa",
                "Land O' Lakes",
                "Wesley Chapel",
                "Zephyrhills",
                "Dade City",
                "Plant City",
                "Riverview",
                "Brandon",
                "Valrico",
                "Lithia",
                "Fish Hawk",
                "Sun City Center",
                "Ruskin",
                "Apollo Beach",
                "Wimauma",
                "Palmetto",
                "Ellenton",
                "Parrish",
                "Terra Ceia",
                "Anna Maria",
                "Longboat Key",
                "Venice",
                "North Port",
                "Englewood",
                "Port Charlotte",
                "Punta Gorda",
                "Arcadia",
                "Wauchula",
                "Sebring",
                "Avon Park",
                "Lake Placid",
                "Clewiston",
                "LaBelle",
                "Moore Haven",
                "Immokalee",
                "Everglades City",
                "Marco Island",
                "Bonita Springs",
                "Estero",
                "Sanibel",
                "Captiva",
                "Fort Myers Beach",
                "Cape Coral",
                "Lehigh Acres",
                "Alva",
                "Labelle",
                "Pahokee",
                "Belle Glade",
                "South Bay",
                "Clewiston",
                "Okeechobee",
                "Indiantown",
                "Port Salerno",
                "Hobe Sound",
                "Tequesta",
                "Juno Beach",
                "North Palm Beach",
                "Palm Beach Gardens",
                "Riviera Beach",
                "Lake Park",
                "Mangonia Park",
                "West Palm Beach",
                "Greenacres",
                "Lake Clarke Shores",
                "Lantana",
                "Hypoluxo",
                "Boynton Beach",
                "Ocean Ridge",
                "Gulf Stream",
                "Delray Beach",
                "Highland Beach",
                "Boca Raton",
                "Deerfield Beach",
                "Hillsboro Beach",
                "Lighthouse Point",
                "Pompano Beach",
                "Lauderdale-by-the-Sea",
                "Sea Ranch Lakes",
                "Lauderdale Lakes",
                "Lauderhill",
                "Tamarac",
                "North Lauderdale",
                "Coconut Creek",
                "Margate",
                "Parkland",
                "Coral Springs",
                "Tamarac",
            ],
            "GA": [
                "Atlanta",
                "Savannah",
                "Augusta",
                "Columbus",
                "Athens",
                "Sandy Springs",
                "Roswell",
                "Macon",
                "Johns Creek",
                "Albany",
                "Warner Robins",
                "Alpharetta",
                "Marietta",
                "Valdosta",
                "Smyrna",
            ],
        }
        return major_cities_map.get(state, [])

    def _search_stores(
        self, query: str, state: Optional[str], seen_store_ids: set
    ) -> List[Dict]:
        """Internal method to search for stores with a specific query"""
        stores = []

        try:
            # Use the new Places API (New)
            headers = {
                "Content-Type": "application/json",
                "X-Goog-Api-Key": self.api_key,
                "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress,places.location,places.addressComponents",
            }

            payload = {
                "textQuery": query,
                # Removed includedType to get all locations (not just grocery stores)
                "maxResultCount": 20,
            }

            response = requests.post(self.base_url, json=payload, headers=headers)
            response.raise_for_status()

            data = response.json()
            places = data.get("places", [])

            # Process results and track seen stores
            new_stores = self._process_places_results_new(places, state)
            for store in new_stores:
                store_id = store.get("store_number") or store.get("address", "")
                if store_id and store_id not in seen_store_ids:
                    stores.append(store)
                    seen_store_ids.add(store_id)

            # Handle pagination - get ALL pages (no limit)
            next_page_token = data.get("nextPageToken")
            page_count = 0
            max_pages = 100  # Safety limit (20 stores/page = 2000 max stores per state)

            while next_page_token and page_count < max_pages:
                import time

                # Random delay between 2-4 seconds to avoid rate limits
                time.sleep(2 + random.uniform(0, 2))

                payload["pageToken"] = next_page_token
                response = requests.post(self.base_url, json=payload, headers=headers)
                response.raise_for_status()

                data = response.json()
                places = data.get("places", [])
                if not places:
                    break  # No more results

                # Process and deduplicate
                new_stores = self._process_places_results_new(places, state)
                for store in new_stores:
                    store_id = store.get("store_number") or store.get("address", "")
                    if store_id and store_id not in seen_store_ids:
                        stores.append(store)
                        seen_store_ids.add(store_id)

                next_page_token = data.get("nextPageToken")
                page_count += 1

                logger.debug(
                    f"Fetched page {page_count + 1}, total stores so far: {len(stores)}"
                )

            logger.info(f"Found {len(stores)} Publix stores")

        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP Error: {e.response.status_code}"
            try:
                error_data = e.response.json()
                error_msg += (
                    f" - {error_data.get('error', {}).get('message', 'Unknown error')}"
                )
            except:
                error_msg += f" - {e.response.text[:200]}"
            logger.error(f"Error scraping Publix stores: {error_msg}")
        except Exception as e:
            logger.error(f"Error scraping Publix stores: {e}", exc_info=True)

        return stores

    def _process_places_results_new(
        self, places: List[Dict], state: Optional[str] = None
    ) -> List[Dict]:
        """Process a batch of place results from Places API (New)"""
        stores = []

        for place in places:
            try:
                place_id = place.get("id", "")
                address = place.get("formattedAddress", "")
                location = place.get("location", {})
                address_components = place.get("addressComponents", [])

                # Parse address components
                city = ""
                state_code = ""
                zip_code = ""

                for component in address_components:
                    types = component.get("types", [])
                    if "locality" in types or "sublocality" in types:
                        city = component.get("longText", "") or component.get(
                            "shortText", ""
                        )
                    elif "administrative_area_level_1" in types:
                        state_code = component.get("shortText", "")
                    elif "postal_code" in types:
                        zip_code = component.get("longText", "") or component.get(
                            "shortText", ""
                        )

                # Fallback to parsing formatted address if components missing
                if not city or not state_code:
                    address_parts = address.split(",")
                    if len(address_parts) >= 3:
                        city = address_parts[-3].strip()
                    if len(address_parts) >= 2:
                        state_code = address_parts[-2].strip().split()[0]

                # Filter by state if specified
                if state and state_code != state:
                    continue

                store = {
                    "store_number": place_id[:10] if place_id else None,
                    "address": address,
                    "city": city,
                    "state": state_code,
                    "zip_code": zip_code,
                    "latitude": location.get("latitude"),
                    "longitude": location.get("longitude"),
                    "square_feet": None,  # Not available from Places API
                }
                stores.append(store)

            except Exception as e:
                logger.warning(
                    f"Error processing place {place.get('id', 'unknown')}: {e}"
                )
                continue

        return stores


class CompetitorScraperGooglePlaces:
    """Scraper for competitor stores using Google Places API (New)"""

    def __init__(self):
        self.api_key = os.getenv("GOOGLE_PLACES_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_PLACES_API_KEY not set in environment")

        # Use the new Places API endpoint
        self.base_url = "https://places.googleapis.com/v1/places:searchText"

    def scrape_walmart_stores(self, state: Optional[str] = None) -> List[Dict]:
        """Scrape Walmart stores"""
        return self._scrape_competitor("Walmart", state)

    def scrape_kroger_stores(self, state: Optional[str] = None) -> List[Dict]:
        """Scrape Kroger stores"""
        return self._scrape_competitor("Kroger", state)

    def scrape_chickfila_stores(self, state: Optional[str] = None) -> List[Dict]:
        """Scrape Chick-fil-A stores"""
        return self._scrape_competitor("Chick-fil-A", state)

    def scrape_target_stores(self, state: Optional[str] = None) -> List[Dict]:
        """Scrape Target stores"""
        return self._scrape_competitor("Target", state)

    def scrape_costco_stores(self, state: Optional[str] = None) -> List[Dict]:
        """Scrape Costco stores"""
        return self._scrape_competitor("Costco", state)

    def _scrape_competitor(self, name: str, state: Optional[str] = None) -> List[Dict]:
        """Generic competitor scraper using Places API (New)"""
        stores = []

        query = name
        if state:
            query += f" in {state}"

        logger.info(f"Searching Google Places API (New) for: {query}")

        try:
            headers = {
                "Content-Type": "application/json",
                "X-Goog-Api-Key": self.api_key,
                "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress,places.location,places.addressComponents",
            }

            payload = {
                "textQuery": query,
                # Removed includedType to get all locations (not just grocery stores)
                "maxResultCount": 20,
            }

            response = requests.post(self.base_url, json=payload, headers=headers)
            response.raise_for_status()

            data = response.json()
            places = data.get("places", [])

            # Process results
            stores.extend(self._process_competitor_results_new(places, state))

            # Handle pagination - get ALL pages (no limit)
            next_page_token = data.get("nextPageToken")
            page_count = 0
            max_pages = 100  # Safety limit (20 stores/page = 2000 max stores per state)

            while next_page_token and page_count < max_pages:
                import time

                time.sleep(2)

                payload["pageToken"] = next_page_token
                response = requests.post(self.base_url, json=payload, headers=headers)
                response.raise_for_status()

                data = response.json()
                places = data.get("places", [])
                stores.extend(self._process_competitor_results_new(places, state))

                next_page_token = data.get("nextPageToken")
                page_count += 1

            logger.info(f"Found {len(stores)} {name} stores")

        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP Error: {e.response.status_code}"
            try:
                error_data = e.response.json()
                error_msg += (
                    f" - {error_data.get('error', {}).get('message', 'Unknown error')}"
                )
            except:
                error_msg += f" - {e.response.text[:200]}"
            logger.error(f"Error scraping {name} stores: {error_msg}")
        except Exception as e:
            logger.error(f"Error scraping {name} stores: {e}", exc_info=True)

        return stores

    def _process_competitor_results_new(
        self, places: List[Dict], state: Optional[str] = None
    ) -> List[Dict]:
        """Process competitor place results from Places API (New)"""
        stores = []

        for place in places:
            try:
                address = place.get("formattedAddress", "")
                location = place.get("location", {})
                address_components = place.get("addressComponents", [])

                # Parse address components
                city = ""
                state_code = ""
                zip_code = ""

                for component in address_components:
                    types = component.get("types", [])
                    if "locality" in types or "sublocality" in types:
                        city = component.get("longText", "") or component.get(
                            "shortText", ""
                        )
                    elif "administrative_area_level_1" in types:
                        state_code = component.get("shortText", "")
                    elif "postal_code" in types:
                        zip_code = component.get("longText", "") or component.get(
                            "shortText", ""
                        )

                # Fallback parsing
                if not city or not state_code:
                    address_parts = address.split(",")
                    if len(address_parts) >= 3:
                        city = address_parts[-3].strip()
                    if len(address_parts) >= 2:
                        state_code = address_parts[-2].strip().split()[0]

                # Filter by state if specified
                if state and state_code != state:
                    continue

                store = {
                    "address": address,
                    "city": city,
                    "state": state_code,
                    "zip_code": zip_code,
                    "latitude": location.get("latitude"),
                    "longitude": location.get("longitude"),
                    "square_feet": None,
                }
                stores.append(store)

            except Exception as e:
                logger.warning(f"Error processing competitor place: {e}")
                continue

        return stores
