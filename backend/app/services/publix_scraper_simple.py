"""
Simpler Publix scraper using requests and BeautifulSoup

This attempts to scrape Publix stores without Selenium first.
If the site requires JavaScript, it will fall back to Selenium.
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import re
import logging
import json

logger = logging.getLogger(__name__)


class PublixScraperSimple:
    """Simple scraper using requests (no browser needed)"""

    def __init__(self):
        self.base_url = "https://www.publix.com"
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            }
        )

    def scrape_stores(self, state: Optional[str] = None) -> List[Dict]:
        """
        Scrape Publix stores - tries simple requests first, falls back to Selenium

        Args:
            state: State code (e.g., "KY", "FL")

        Returns:
            List of store dictionaries
        """
        stores = []

        # Try to find Publix's store locator API endpoint
        # Many sites use an API endpoint even if the UI is JavaScript-based
        api_endpoints = [
            f"{self.base_url}/api/stores",
            f"{self.base_url}/api/store-locator",
            f"{self.base_url}/shopping/api/stores",
            f"{self.base_url}/shopping/api/store-locator",
        ]

        # Try API endpoints first
        for endpoint in api_endpoints:
            try:
                params = {"state": state} if state else {}
                response = self.session.get(endpoint, params=params, timeout=10)
                if response.status_code == 200:
                    try:
                        data = response.json()
                        stores = self._parse_api_response(data)
                        if stores:
                            logger.info(f"Found {len(stores)} stores via API endpoint")
                            return stores
                    except json.JSONDecodeError:
                        pass
            except Exception as e:
                logger.debug(f"API endpoint {endpoint} failed: {e}")

        # Try scraping the store locator page
        try:
            url = f"{self.base_url}/shopping/store-locator"
            if state:
                url += f"?state={state}"

            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                stores = self._parse_html(response.text, state)
                if stores:
                    logger.info(f"Found {len(stores)} stores via HTML parsing")
                    return stores
        except Exception as e:
            logger.warning(f"HTML scraping failed: {e}")

        # Fall back to Playwright if available (better than Selenium on macOS)
        if not stores:
            try:
                from app.services.publix_scraper_playwright import (
                    PublixScraperPlaywright,
                )

                playwright_scraper = PublixScraperPlaywright(headless=True)
                stores = playwright_scraper.scrape_stores(state=state)
                if stores:
                    logger.info(f"Found {len(stores)} stores via Playwright")
            except ImportError:
                # Try Selenium as last resort
                try:
                    from app.services.publix_scraper import PublixScraperDirect

                    direct_scraper = PublixScraperDirect(headless=True)
                    stores = direct_scraper.scrape_stores(state=state)
                    if stores:
                        logger.info(f"Found {len(stores)} stores via Selenium")
                except Exception as e:
                    logger.warning(f"Browser scraper fallback failed: {e}")
            except Exception as e:
                logger.warning(f"Playwright fallback failed: {e}")

        return stores

    def _parse_api_response(self, data: dict) -> List[Dict]:
        """Parse JSON API response"""
        stores = []

        # Handle different possible response structures
        store_list = (
            data.get("stores", [])
            or data.get("locations", [])
            or data.get("results", [])
        )

        if isinstance(data, list):
            store_list = data

        for item in store_list:
            store = {
                "store_number": item.get("storeNumber")
                or item.get("id")
                or item.get("store_id"),
                "address": item.get("address")
                or item.get("streetAddress")
                or item.get("street_address"),
                "city": item.get("city"),
                "state": item.get("state")
                or item.get("stateCode")
                or item.get("state_code"),
                "zip_code": item.get("zipCode")
                or item.get("zip")
                or item.get("postalCode"),
                "latitude": item.get("latitude") or item.get("lat"),
                "longitude": item.get("longitude")
                or item.get("lng")
                or item.get("lon"),
                "square_feet": item.get("squareFeet")
                or item.get("square_feet")
                or item.get("size"),
            }

            # Only add if we have essential fields
            if store["address"] and store["city"]:
                stores.append(store)

        return stores

    def _parse_html(self, html: str, state: Optional[str] = None) -> List[Dict]:
        """Parse HTML page for store data"""
        stores = []
        soup = BeautifulSoup(html, "html.parser")

        # Look for JSON data embedded in script tags
        script_tags = soup.find_all("script", type="application/json")
        for script in script_tags:
            try:
                data = json.loads(script.string)
                parsed = self._parse_api_response(data)
                if parsed:
                    stores.extend(parsed)
            except (json.JSONDecodeError, AttributeError):
                pass

        # Look for data attributes
        store_elements = soup.find_all(attrs={"data-store-id": True}) or soup.find_all(
            class_=re.compile(r"store", re.I)
        )

        for element in store_elements:
            store = self._extract_store_from_element(element, state)
            if store:
                stores.append(store)

        # Look for addresses in the page
        address_pattern = re.compile(
            r"(\d+[\s\w]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr)[\s\w,]+)",
            re.IGNORECASE,
        )

        addresses = address_pattern.findall(html)
        for addr in addresses[:20]:  # Limit to avoid duplicates
            city_state_match = re.search(
                r"([A-Za-z\s]+),\s*([A-Z]{2})\s+(\d{5})",
                html[html.find(addr) : html.find(addr) + 200],
            )
            if city_state_match:
                store = {
                    "store_number": None,
                    "address": addr.strip(),
                    "city": city_state_match.group(1).strip(),
                    "state": city_state_match.group(2),
                    "zip_code": city_state_match.group(3),
                    "latitude": None,
                    "longitude": None,
                    "square_feet": None,
                }
                stores.append(store)

        return stores

    def _extract_store_from_element(
        self, element, state: Optional[str] = None
    ) -> Optional[Dict]:
        """Extract store data from an HTML element"""
        try:
            store_id = element.get("data-store-id") or element.get("id")
            text = element.get_text()

            # Extract address
            address_match = re.search(
                r"(\d+[\s\w]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr)[\s\w,]+)",
                text,
                re.IGNORECASE,
            )

            city_state_match = re.search(r"([A-Za-z\s]+),\s*([A-Z]{2})\s+(\d{5})", text)

            if address_match and city_state_match:
                return {
                    "store_number": store_id,
                    "address": address_match.group(1).strip(),
                    "city": city_state_match.group(1).strip(),
                    "state": city_state_match.group(2),
                    "zip_code": city_state_match.group(3),
                    "latitude": element.get("data-lat") or None,
                    "longitude": element.get("data-lng") or None,
                    "square_feet": None,
                }
        except Exception as e:
            logger.debug(f"Error extracting store from element: {e}")

        return None
