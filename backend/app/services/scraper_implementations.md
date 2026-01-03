# Scraper Implementation Guide

The scrapers in `scraper.py` are currently placeholders. Here's how to implement them:

## 1. Publix Store Scraper

Publix has a store locator API. Options:

### Option A: Use Publix Store Locator API
```python
def scrape_stores(self, state: Optional[str] = None) -> List[Dict]:
    """Scrape Publix store locations using their store locator"""
    stores = []
    # Publix store locator endpoint (may need to reverse engineer)
    url = "https://www.publix.com/shopping/store-locator"
    # Use requests + BeautifulSoup or Selenium to extract store data
    return stores
```

### Option B: Use Google Places API
```python
def scrape_stores(self, state: Optional[str] = None) -> List[Dict]:
    """Use Google Places API to find Publix stores"""
    import googlemaps
    gmaps = googlemaps.Client(key=os.getenv("GOOGLE_PLACES_API_KEY"))
    
    query = "Publix" + (f" in {state}" if state else "")
    places = gmaps.places(query=query, type="grocery_or_supermarket")
    
    stores = []
    for place in places.get("results", []):
        stores.append({
            "store_number": place.get("place_id", ""),
            "address": place.get("formatted_address", ""),
            "city": extract_city(place.get("formatted_address", "")),
            "state": state or extract_state(place.get("formatted_address", "")),
            "latitude": place["geometry"]["location"]["lat"],
            "longitude": place["geometry"]["location"]["lng"],
            "square_feet": None,  # Not available from Places API
        })
    return stores
```

## 2. Competitor Scrapers

Similar approach - use Google Places API or scrape competitor websites.

## 3. Demographics Service

Use US Census Bureau API:

```python
def get_demographics(self, city: str, state: str) -> Optional[Dict]:
    """Fetch from Census API"""
    import requests
    
    # Get state FIPS code
    state_fips = get_state_fips(state)
    
    # Census API endpoint
    url = f"https://api.census.gov/data/2021/acs/acs5"
    params = {
        "get": "B01001_001E,B19013_001E",  # Population, Median Income
        "for": f"place:{get_place_code(city, state)}",
        "in": f"state:{state_fips}",
        "key": os.getenv("CENSUS_API_KEY")
    }
    
    response = requests.get(url, params=params)
    # Parse and return demographics
    return demographics_dict
```

## 4. Zoning Records

Scrape city/municipality planning commission websites or use APIs like:
- CityData APIs
- Municipal planning department websites
- Commercial real estate APIs (LoopNet, CoStar)

