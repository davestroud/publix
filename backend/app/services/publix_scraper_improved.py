"""
Improved Publix scraper - tries multiple strategies to extract store data

This scraper uses multiple approaches:
1. Find Publix's internal API endpoint
2. Extract from JavaScript data
3. Parse HTML elements with better regex
4. Use Playwright to interact with the page
"""

import time
import logging
from typing import List, Dict, Optional
import re
import json

logger = logging.getLogger(__name__)

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


class PublixScraperImproved:
    """Improved scraper with multiple extraction strategies"""

    def __init__(self, headless: bool = True):
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError("Playwright not installed")

        self.base_url = "https://www.publix.com/shopping/store-locator"
        self.headless = headless

    def scrape_stores(self, state: Optional[str] = None) -> List[Dict]:
        """Scrape Publix stores using multiple strategies"""
        stores = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            page = browser.new_page()

            try:
                logger.info(f"Loading Publix store locator...")
                page.goto(self.base_url, wait_until="domcontentloaded", timeout=60000)
                time.sleep(5)  # Give JavaScript time to load

                # Strategy 1: Try to find API endpoint in network requests
                stores = self._extract_from_network(page, state)
                if stores:
                    logger.info(f"Found {len(stores)} stores via network API")
                    browser.close()
                    return stores

                # Strategy 2: Extract from JavaScript variables/data
                stores = self._extract_from_js_variables(page)
                if stores:
                    logger.info(f"Found {len(stores)} stores via JavaScript variables")
                    browser.close()
                    return stores

                # Strategy 3: Extract from embedded JSON in script tags
                stores = self._extract_from_script_tags(page)
                if stores:
                    logger.info(f"Found {len(stores)} stores via script tags")
                    browser.close()
                    return stores

                # Strategy 4: Interact with search and extract from results
                if state:
                    stores = self._search_and_extract(page, state)
                    if stores:
                        logger.info(
                            f"Found {len(stores)} stores via search interaction"
                        )
                        browser.close()
                        return stores

                # Strategy 5: Parse all visible text for addresses
                stores = self._extract_from_page_text(page, state)
                if stores:
                    logger.info(f"Found {len(stores)} stores via text parsing")

            except Exception as e:
                logger.error(f"Error during scraping: {e}", exc_info=True)
            finally:
                browser.close()

        return stores

    def _extract_from_network(self, page, state: Optional[str]) -> List[Dict]:
        """Try to intercept API calls"""
        stores = []

        try:
            # Listen for network responses
            api_responses = []

            def handle_response(response):
                url = response.url
                if any(
                    keyword in url.lower()
                    for keyword in ["store", "location", "api", "locator"]
                ):
                    try:
                        api_responses.append(response.json())
                    except:
                        pass

            page.on("response", handle_response)

            # Trigger search if state provided
            if state:
                try:
                    search_input = page.query_selector(
                        "input[type='search'], input[placeholder*='search' i], input[placeholder*='zip' i]"
                    )
                    if search_input:
                        search_input.fill(state)
                        time.sleep(1)
                        search_button = page.query_selector(
                            "button[type='submit'], button:has-text('Search'), button:has-text('Find')"
                        )
                        if search_button:
                            search_button.click()
                            page.wait_for_load_state("networkidle", timeout=10000)
                            time.sleep(3)
                except:
                    pass

            # Check collected responses
            for response_data in api_responses:
                if isinstance(response_data, dict):
                    parsed = self._parse_api_response(response_data)
                    if parsed:
                        stores.extend(parsed)

        except Exception as e:
            logger.debug(f"Network extraction failed: {e}")

        return stores

    def _extract_from_js_variables(self, page) -> List[Dict]:
        """Extract from JavaScript variables"""
        stores = []

        try:
            js_code = """
            () => {
                const results = [];
                
                // Check window object
                const windowKeys = Object.keys(window);
                for (let key of windowKeys) {
                    if (key.toLowerCase().includes('store') || key.toLowerCase().includes('location')) {
                        const obj = window[key];
                        if (Array.isArray(obj) && obj.length > 0) {
                            if (obj[0].address || obj[0].city || obj[0].latitude) {
                                return obj;
                            }
                        }
                    }
                }
                
                // Check React/Redux state
                if (window.__REDUX_STATE__) {
                    const state = window.__REDUX_STATE__;
                    const stateStr = JSON.stringify(state);
                    if (stateStr.includes('store') || stateStr.includes('location')) {
                        // Try to find stores in state
                        function findStores(obj, path = '') {
                            if (Array.isArray(obj)) {
                                if (obj.length > 0 && obj[0].address) {
                                    return obj;
                                }
                                for (let item of obj) {
                                    const found = findStores(item, path);
                                    if (found) return found;
                                }
                            } else if (typeof obj === 'object' && obj !== null) {
                                for (let key in obj) {
                                    if (key.toLowerCase().includes('store') || key.toLowerCase().includes('location')) {
                                        const found = findStores(obj[key], path + '.' + key);
                                        if (found) return found;
                                    } else {
                                        const found = findStores(obj[key], path + '.' + key);
                                        if (found) return found;
                                    }
                                }
                            }
                            return null;
                        }
                        const found = findStores(state);
                        if (found) return found;
                    }
                }
                
                return null;
            }
            """

            js_data = page.evaluate(js_code)

            if js_data:
                stores = self._parse_api_response(
                    {"stores": js_data} if isinstance(js_data, list) else js_data
                )

        except Exception as e:
            logger.debug(f"JS variable extraction failed: {e}")

        return stores

    def _extract_from_script_tags(self, page) -> List[Dict]:
        """Extract from JSON in script tags"""
        stores = []

        try:
            script_content = page.evaluate(
                """
                () => {
                    const scripts = document.querySelectorAll('script[type="application/json"], script[type="application/ld+json"]');
                    const results = [];
                    for (let script of scripts) {
                        try {
                            const data = JSON.parse(script.textContent);
                            results.push(data);
                        } catch(e) {}
                    }
                    return results;
                }
            """
            )

            for data in script_content:
                parsed = self._parse_api_response(data)
                if parsed:
                    stores.extend(parsed)

        except Exception as e:
            logger.debug(f"Script tag extraction failed: {e}")

        return stores

    def _search_and_extract(self, page, state: str) -> List[Dict]:
        """Interact with search and extract results"""
        stores = []

        try:
            # Try to find and use search
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
                    search_input = page.query_selector(selector)
                    if search_input:
                        search_input.fill(state)
                        time.sleep(1)

                        # Click search
                        search_button = page.query_selector(
                            "button[type='submit'], button:has-text('Search'), button:has-text('Find'), .search-button"
                        )
                        if search_button:
                            search_button.click()
                            page.wait_for_load_state("domcontentloaded", timeout=10000)
                            time.sleep(3)

                            # Now extract from updated page
                            stores = self._extract_from_js_variables(page)
                            if not stores:
                                stores = self._extract_from_script_tags(page)
                            break
                except:
                    continue

        except Exception as e:
            logger.debug(f"Search interaction failed: {e}")

        return stores

    def _extract_from_page_text(self, page, state: Optional[str]) -> List[Dict]:
        """Extract stores by parsing page text for addresses"""
        stores = []

        try:
            # Get all text content
            page_text = page.evaluate("() => document.body.innerText")

            # Find addresses with Publix context
            address_pattern = re.compile(
                r"(\d+\s+[\w\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Way|Circle|Cir|Court|Ct)[\s\w,]+)",
                re.IGNORECASE,
            )

            # Find city, state, zip patterns
            city_state_pattern = re.compile(
                r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*([A-Z]{2})\s+(\d{5}(?:-\d{4})?)",
                re.MULTILINE,
            )

            addresses = address_pattern.findall(page_text)
            city_states = city_state_pattern.findall(page_text)

            # Match addresses with cities
            for addr in addresses[:100]:  # Limit to avoid duplicates
                addr_lower = addr.lower()
                # Find nearby city/state
                addr_pos = page_text.find(addr)
                nearby_text = page_text[max(0, addr_pos - 200) : addr_pos + 500]

                city_match = city_state_pattern.search(nearby_text)
                if city_match and (
                    "publix" in nearby_text.lower() or "store" in nearby_text.lower()
                ):
                    store = {
                        "store_number": None,
                        "address": addr.strip(),
                        "city": city_match.group(1).strip(),
                        "state": city_match.group(2),
                        "zip_code": city_match.group(3),
                        "latitude": None,
                        "longitude": None,
                        "square_feet": None,
                    }

                    # Filter by state if provided
                    if not state or store["state"] == state:
                        stores.append(store)

        except Exception as e:
            logger.debug(f"Text extraction failed: {e}")

        return stores

    def _parse_api_response(self, data: dict) -> List[Dict]:
        """Parse API response data"""
        stores = []

        # Handle different response structures
        store_list = []

        if isinstance(data, list):
            store_list = data
        elif isinstance(data, dict):
            store_list = (
                data.get("stores", [])
                or data.get("locations", [])
                or data.get("results", [])
                or data.get("data", {}).get("stores", [])
                or data.get("data", {}).get("locations", [])
            )

        for item in store_list:
            if not isinstance(item, dict):
                continue

            # Try to extract address components
            address = (
                item.get("address")
                or item.get("streetAddress")
                or item.get("street_address")
                or item.get("fullAddress")
            )

            city = item.get("city")
            state_code = (
                item.get("state") or item.get("stateCode") or item.get("state_code")
            )

            # Skip if missing essential data
            if not address or not city or not state_code:
                continue

            store = {
                "store_number": (
                    item.get("storeNumber")
                    or item.get("id")
                    or item.get("store_id")
                    or item.get("storeId")
                ),
                "address": address,
                "city": city,
                "state": state_code,
                "zip_code": (
                    item.get("zipCode")
                    or item.get("zip")
                    or item.get("postalCode")
                    or item.get("postal_code")
                ),
                "latitude": (
                    item.get("latitude")
                    or item.get("lat")
                    or (
                        item.get("coordinates", {}).get("lat")
                        if isinstance(item.get("coordinates"), dict)
                        else None
                    )
                ),
                "longitude": (
                    item.get("longitude")
                    or item.get("lng")
                    or item.get("lon")
                    or (
                        item.get("coordinates", {}).get("lng")
                        if isinstance(item.get("coordinates"), dict)
                        else None
                    )
                ),
                "square_feet": (
                    item.get("squareFeet")
                    or item.get("square_feet")
                    or item.get("size")
                ),
            }

            stores.append(store)

        return stores
