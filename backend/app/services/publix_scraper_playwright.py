"""
Publix scraper using Playwright (recommended alternative to Selenium)

Playwright handles browser installation automatically and works better on macOS.
"""

import time
import logging
from typing import List, Dict, Optional
import re

logger = logging.getLogger(__name__)

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logger.warning(
        "Playwright not installed. Install with: poetry add playwright && poetry run playwright install"
    )


class PublixScraperPlaywright:
    """Publix scraper using Playwright (better than Selenium on macOS)"""

    def __init__(self, headless: bool = True):
        """
        Initialize the scraper

        Args:
            headless: Run browser in headless mode (default: True)
        """
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError(
                "Playwright not installed. Install with: poetry add playwright && poetry run playwright install"
            )

        self.base_url = "https://www.publix.com/shopping/store-locator"
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.page = None

    def scrape_stores(self, state: Optional[str] = None) -> List[Dict]:
        """
        Scrape Publix store locations

        Args:
            state: State code (e.g., "KY", "FL") or None for all states

        Returns:
            List of store dictionaries
        """
        stores = []

        try:
            self.playwright = sync_playwright().start()

            # Use Chromium (or firefox/webkit)
            self.browser = self.playwright.chromium.launch(headless=self.headless)
            self.page = self.browser.new_page()

            # Set user agent
            self.page.set_extra_http_headers(
                {
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
                }
            )

            logger.info(f"Scraping Publix stores{' for ' + state if state else ''}")

            # Navigate to store locator (increase timeout, use domcontentloaded instead of networkidle)
            self.page.goto(self.base_url, wait_until="domcontentloaded", timeout=60000)
            time.sleep(3)  # Give page time to load JavaScript

            # Try to interact with search if state provided
            if state:
                try:
                    # Look for search input
                    search_selectors = [
                        "input[type='search']",
                        "input[placeholder*='search' i]",
                        "input[placeholder*='zip' i]",
                        "input[placeholder*='city' i]",
                        "#store-search",
                        ".store-search",
                    ]

                    for selector in search_selectors:
                        try:
                            search_input = self.page.query_selector(selector)
                            if search_input:
                                search_input.fill(state)
                                time.sleep(1)

                                # Find and click search button
                                search_button = self.page.query_selector(
                                    "button[type='submit'], button:has-text('Search')"
                                )
                                if search_button:
                                    search_button.click()
                                    self.page.wait_for_load_state("networkidle")
                                    time.sleep(2)
                                break
                        except Exception:
                            continue
                except Exception as e:
                    logger.debug(f"Could not interact with search: {e}")

            # Extract stores
            stores = self._extract_stores()

            logger.info(f"Found {len(stores)} Publix stores")

        except Exception as e:
            logger.error(f"Error scraping Publix stores: {e}", exc_info=True)
        finally:
            self._cleanup()

        return stores

    def _extract_stores(self) -> List[Dict]:
        """Extract store information from the page"""
        stores = []

        try:
            # Wait for content to load
            time.sleep(2)

            # Try to extract from JavaScript data first
            js_stores = self._extract_from_js()
            if js_stores:
                return js_stores

            # Extract from HTML elements
            store_elements = self.page.query_selector_all(
                ".store-location, .store-item, [data-store-id], .location-card, .store-card"
            )

            if not store_elements:
                # Try broader search
                all_elements = self.page.query_selector_all("div, article, li")
                store_elements = [
                    el
                    for el in all_elements
                    if "publix" in el.inner_text().lower()
                    or "store" in el.inner_text().lower()
                ]

            logger.info(f"Found {len(store_elements)} potential store elements")

            for element in store_elements[:50]:
                try:
                    store_data = self._parse_store_element(element)
                    if store_data:
                        stores.append(store_data)
                except Exception as e:
                    logger.debug(f"Error parsing store element: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error extracting stores: {e}")

        return stores

    def _extract_from_js(self) -> List[Dict]:
        """Extract store data from JavaScript variables"""
        stores = []

        try:
            # Try to find store data in JavaScript
            js_code = """
            () => {
                // Look for common variable names
                if (typeof window.stores !== 'undefined') return window.stores;
                if (typeof window.storeLocations !== 'undefined') return window.storeLocations;
                if (typeof window.storeData !== 'undefined') return window.storeData;
                if (typeof window.locations !== 'undefined') return window.locations;
                
                // Look in React/Redux state
                if (window.__REDUX_STATE__) {
                    const state = window.__REDUX_STATE__;
                    if (state.stores) return state.stores;
                    if (state.locations) return state.locations;
                }
                
                // Look for data in script tags
                const scripts = document.querySelectorAll('script[type="application/json"]');
                for (let script of scripts) {
                    try {
                        const data = JSON.parse(script.textContent);
                        if (data.stores || data.locations) {
                            return data.stores || data.locations;
                        }
                    } catch(e) {}
                }
                
                return null;
            }
            """

            js_data = self.page.evaluate(js_code)

            if js_data:
                for item in js_data:
                    store = {
                        "store_number": item.get("storeNumber") or item.get("id"),
                        "address": item.get("address") or item.get("streetAddress"),
                        "city": item.get("city"),
                        "state": item.get("state") or item.get("stateCode"),
                        "zip_code": item.get("zipCode") or item.get("zip"),
                        "latitude": item.get("latitude") or item.get("lat"),
                        "longitude": item.get("longitude")
                        or item.get("lng")
                        or item.get("lon"),
                        "square_feet": item.get("squareFeet") or item.get("size"),
                    }
                    if store["address"] and store["city"]:
                        stores.append(store)

        except Exception as e:
            logger.debug(f"Error extracting from JS: {e}")

        return stores

    def _parse_store_element(self, element) -> Optional[Dict]:
        """Parse a single store element"""
        try:
            text = element.inner_text()

            # More lenient - just check if it has enough text
            if len(text) < 15:
                return None

            # Extract address
            address_match = re.search(
                r"(\d+[\s\w]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr)[\s\w,]+)",
                text,
                re.IGNORECASE,
            )

            # Extract city, state, zip
            city_state_zip = re.search(
                r"([A-Za-z\s]+),\s*([A-Z]{2})\s+(\d{5}(?:-\d{4})?)", text
            )

            # Get coordinates from data attributes
            lat = element.get_attribute("data-lat") or element.get_attribute(
                "data-latitude"
            )
            lon = element.get_attribute("data-lng") or element.get_attribute(
                "data-longitude"
            )

            if lat and lon:
                try:
                    lat = float(lat)
                    lon = float(lon)
                except ValueError:
                    lat = lon = None

            # More flexible - try to extract address even if pattern doesn't match exactly
            if not address_match:
                # Try simpler pattern
                simple_addr = re.search(r"(\d+\s+[\w\s]{10,60})", text)
                if simple_addr:
                    address = simple_addr.group(1).strip()
                else:
                    return None

            address = address_match.group(1).strip()
            city = city_state_zip.group(1).strip() if city_state_zip else ""
            state_code = city_state_zip.group(2) if city_state_zip else ""
            zip_code = city_state_zip.group(3) if city_state_zip else ""

            # Extract store number
            store_number_match = re.search(r"store[:\s#]*(\d+)", text, re.IGNORECASE)
            store_number = store_number_match.group(1) if store_number_match else None

            store = {
                "store_number": store_number,
                "address": address,
                "city": city,
                "state": state_code,
                "zip_code": zip_code,
                "latitude": lat,
                "longitude": lon,
                "square_feet": None,
            }

            if store["address"] and store["city"] and store["state"]:
                return store

        except Exception as e:
            logger.debug(f"Error parsing store element: {e}")

        return None

    def _cleanup(self):
        """Clean up browser resources"""
        try:
            if self.page:
                self.page.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
        except Exception as e:
            logger.warning(f"Error during cleanup: {e}")
