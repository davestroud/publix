"""
Direct scraper for Publix store locations from their official website

This scraper uses Selenium to interact with Publix's store locator
and extract store information.
"""

import time
import logging
from typing import List, Dict, Optional
from datetime import datetime
import re

logger = logging.getLogger(__name__)

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.common.exceptions import TimeoutException, NoSuchElementException

    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    logger.warning("Selenium not installed. Install with: poetry add selenium")


class PublixScraperDirect:
    """Direct scraper for Publix store locations"""

    def __init__(self, headless: bool = True):
        """
        Initialize the scraper

        Args:
            headless: Run browser in headless mode (default: True)
        """
        if not SELENIUM_AVAILABLE:
            raise ImportError(
                "Selenium not installed. Install with: poetry add selenium"
            )

        self.base_url = "https://www.publix.com/shopping/store-locator"
        self.headless = headless
        self.driver = None

    def _setup_driver(self):
        """Setup Chrome WebDriver"""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        )

        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)
        except Exception as e:
            logger.error(f"Failed to setup Chrome driver: {e}")
            logger.info(
                "Make sure ChromeDriver is installed: brew install chromedriver"
            )
            raise

    def _cleanup_driver(self):
        """Close the browser driver"""
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                logger.warning(f"Error closing driver: {e}")

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
            self._setup_driver()
            logger.info(f"Scraping Publix stores{' for ' + state if state else ''}")

            # Navigate to store locator
            self.driver.get(self.base_url)
            time.sleep(2)  # Wait for page to load

            # Find and interact with search
            try:
                # Look for search input - Publix uses various selectors
                # Try common selectors for store locator search
                search_selectors = [
                    "input[type='search']",
                    "input[placeholder*='search' i]",
                    "input[placeholder*='zip' i]",
                    "input[placeholder*='city' i]",
                    "#store-search",
                    ".store-search",
                    "[data-testid='store-search']",
                ]

                search_input = None
                for selector in search_selectors:
                    try:
                        search_input = self.driver.find_element(
                            By.CSS_SELECTOR, selector
                        )
                        break
                    except NoSuchElementException:
                        continue

                if not search_input:
                    # Try finding by text input
                    search_inputs = self.driver.find_elements(By.TAG_NAME, "input")
                    for inp in search_inputs:
                        if inp.get_attribute("type") in ["text", "search"]:
                            search_input = inp
                            break

                if search_input and state:
                    # Enter state and search
                    search_input.clear()
                    search_input.send_keys(state)
                    time.sleep(1)

                    # Find and click search button
                    search_button_selectors = [
                        "button[type='submit']",
                        "button:contains('Search')",
                        ".search-button",
                        "[data-testid='search-button']",
                    ]

                    for selector in search_button_selectors:
                        try:
                            if ":contains" in selector:
                                # Use XPath for text matching
                                button = self.driver.find_element(
                                    By.XPATH, "//button[contains(text(), 'Search')]"
                                )
                            else:
                                button = self.driver.find_element(
                                    By.CSS_SELECTOR, selector
                                )
                            button.click()
                            break
                        except NoSuchElementException:
                            continue

                    # Wait for results to load
                    time.sleep(3)

                # Extract store data from results
                stores = self._extract_stores()

            except Exception as e:
                logger.error(f"Error interacting with search: {e}")
                # Try to extract stores anyway (maybe page already has results)
                stores = self._extract_stores()

            logger.info(f"Found {len(stores)} Publix stores")

        except Exception as e:
            logger.error(f"Error scraping Publix stores: {e}", exc_info=True)
        finally:
            self._cleanup_driver()

        return stores

    def _extract_stores(self) -> List[Dict]:
        """Extract store information from the page"""
        stores = []

        try:
            # Wait for store results to appear
            # Publix typically shows stores in a list or map markers
            time.sleep(2)

            # Try multiple strategies to find store elements
            store_selectors = [
                ".store-location",
                ".store-item",
                "[data-store-id]",
                ".location-card",
                ".store-card",
                "[class*='store']",
            ]

            store_elements = []
            for selector in store_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        store_elements = elements
                        logger.info(f"Found stores using selector: {selector}")
                        break
                except Exception:
                    continue

            # If no specific store elements found, try to get all clickable elements
            # that might be stores
            if not store_elements:
                # Look for elements with addresses or store info
                all_elements = self.driver.find_elements(
                    By.CSS_SELECTOR, "div, article, li"
                )
                store_elements = [
                    el
                    for el in all_elements
                    if any(
                        keyword in el.text.lower()
                        for keyword in ["publix", "store", "address"]
                    )
                    and len(el.text) > 20  # Filter out small elements
                ]

            logger.info(f"Found {len(store_elements)} potential store elements")

            for element in store_elements[:50]:  # Limit to avoid too many
                try:
                    store_data = self._parse_store_element(element)
                    if store_data:
                        stores.append(store_data)
                except Exception as e:
                    logger.debug(f"Error parsing store element: {e}")
                    continue

            # Alternative: Try to extract from JavaScript data
            if not stores:
                stores = self._extract_from_js_data()

        except Exception as e:
            logger.error(f"Error extracting stores: {e}")

        return stores

    def _parse_store_element(self, element) -> Optional[Dict]:
        """Parse a single store element"""
        try:
            text = element.text

            # Skip if too short or doesn't look like a store
            if len(text) < 20 or "publix" not in text.lower():
                return None

            # Extract address (common patterns)
            address_match = re.search(
                r"(\d+[\s\w]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Way|Circle|Cir)[\s\w,]+)",
                text,
                re.IGNORECASE,
            )

            # Extract city, state, zip
            city_state_zip = re.search(
                r"([A-Za-z\s]+),\s*([A-Z]{2})\s+(\d{5}(?:-\d{4})?)", text
            )

            # Extract phone
            phone_match = re.search(r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text)

            # Try to get coordinates from data attributes or links
            lat = None
            lon = None

            # Check for data attributes
            lat_attr = element.get_attribute("data-lat") or element.get_attribute(
                "data-latitude"
            )
            lon_attr = element.get_attribute("data-lng") or element.get_attribute(
                "data-longitude"
            )

            if lat_attr and lon_attr:
                try:
                    lat = float(lat_attr)
                    lon = float(lon_attr)
                except ValueError:
                    pass

            # Check for Google Maps link
            if not lat or not lon:
                map_links = element.find_elements(
                    By.CSS_SELECTOR,
                    "a[href*='maps.google.com'], a[href*='google.com/maps']",
                )
                for link in map_links:
                    href = link.get_attribute("href")
                    coords = re.search(r"[?&]q=([\d.-]+),([\d.-]+)", href)
                    if coords:
                        lat = float(coords.group(1))
                        lon = float(coords.group(2))
                        break

            if not address_match:
                return None

            address = address_match.group(1).strip()
            city = city_state_zip.group(1).strip() if city_state_zip else ""
            state_code = city_state_zip.group(2) if city_state_zip else ""
            zip_code = city_state_zip.group(3) if city_state_zip else ""

            # Extract store number if available
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
                "square_feet": None,  # Not available from website
            }

            # Only return if we have essential data
            if store["address"] and store["city"] and store["state"]:
                return store

        except Exception as e:
            logger.debug(f"Error parsing store element: {e}")

        return None

    def _extract_from_js_data(self) -> List[Dict]:
        """Try to extract store data from JavaScript variables/data"""
        stores = []

        try:
            # Execute JavaScript to get store data if it's in a JS variable
            js_code = """
            // Try common variable names
            if (typeof stores !== 'undefined') return stores;
            if (typeof storeLocations !== 'undefined') return storeLocations;
            if (typeof storeData !== 'undefined') return storeData;
            if (typeof locations !== 'undefined') return locations;
            
            // Try to find data in window object
            for (let key in window) {
                if (key.toLowerCase().includes('store') || key.toLowerCase().includes('location')) {
                    let obj = window[key];
                    if (Array.isArray(obj) && obj.length > 0 && obj[0].address) {
                        return obj;
                    }
                }
            }
            
            return null;
            """

            js_data = self.driver.execute_script(js_code)

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
            logger.debug(f"Error extracting from JS data: {e}")

        return stores
