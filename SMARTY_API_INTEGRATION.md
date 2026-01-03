# Smarty API Integration for Zoning Records

## Overview

Integrated Smarty API for collecting property and parcel data to support zoning record collection. Smarty provides comprehensive property data including acreage, zoning codes, and property characteristics.

## Setup

### 1. Add API Keys to `.env`

Add your Smarty credentials to `backend/.env`:

```bash
SMARTY_AUTH_ID=your_auth_id_here
SMARTY_API_KEY=your_api_key_here
```

### 2. Smarty API Endpoints Used

- **US Street API**: Address validation and geocoding
  - Endpoint: `https://us-street.api.smarty.com/street-address`
  - Used for: Standardizing addresses before property lookup

- **US Property Data API**: Property details
  - Endpoint: `https://us-property.api.smarty.com/property` (check docs for exact endpoint)
  - Used for: Getting acreage, zoning, property characteristics

- **US Geocoding API**: Address geocoding
  - Endpoint: `https://us-geocoding.api.smarty.com/lookup`
  - Used for: Getting coordinates for addresses

## Authentication

Smarty uses query parameters for authentication:
- `auth-id`: Your SMARTY_AUTH_ID
- `auth-token`: Your SMARTY_API_KEY

Both are automatically added to all requests.

## Implementation

### SmartyService (`smarty_service.py`)

Main service class with methods:
- `geocode_address()` - Geocode addresses to get coordinates
- `get_property_by_address()` - Get property data for specific addresses
- `search_parcels_by_city()` - Search for parcels in a city (framework)
- `batch_get_properties()` - Process multiple addresses

### Integration Points

1. **ZoningScraper** (`scraper.py`)
   - Uses SmartyService to get property data
   - Converts Smarty property data to zoning record format
   - Filters by acreage (15-25 acres)

2. **ParcelService** (`parcel_service.py`)
   - Uses SmartyService for property lookups
   - Gets addresses from collected stores/competitors
   - Filters parcels by acreage range

## Usage

### Get Property Data for an Address

```python
from app.services.smarty_service import SmartyService

smarty = SmartyService()
property_data = smarty.get_property_by_address(
    address="123 Main St",
    city="Lexington",
    state="KY",
    zip_code="40508"
)
```

### Search Parcels in a City

```python
from app.services.parcel_service import ParcelService
from app.services.database import SessionLocal

db = SessionLocal()
parcel_service = ParcelService(db=db)

parcels = parcel_service.get_parcels_by_city(
    city="Lexington",
    state="KY",
    min_acreage=15.0,
    max_acreage=25.0
)
```

### Collect Zoning Records

The `DataCollectorAgent` automatically uses Smarty when collecting zoning records:

```python
from app.agents.data_collector import DataCollectorAgent

collector = DataCollectorAgent(db)
cities = [{"city": "Lexington", "state": "KY"}]
records = collector.collect_zoning_records(cities, min_acreage=15.0, max_acreage=25.0)
```

## Data Structure

### Property Data from Smarty

Smarty Property API returns data including:
- Acreage/lot size
- Zoning codes
- Assessed value
- Owner information
- Property characteristics
- Geographic coordinates

### Zoning Record Format

```python
{
    "parcel_id": "APN or parcel ID",
    "address": "123 Main St",
    "city": "Lexington",
    "state": "KY",
    "latitude": 38.0406,
    "longitude": -84.5037,
    "acreage": 18.5,
    "zoning_status": "unknown",
    "permit_type": "commercial",
    "description": "Commercial parcel",
    "additional_data": {...}  # Full Smarty property data
}
```

## Notes

1. **API Endpoint Structure**: Smarty Property API endpoint may vary. Check https://www.smarty.com/docs for exact endpoint structure.

2. **City-Wide Searches**: Smarty may not support direct city-wide property searches. Current implementation:
   - Uses addresses from collected stores/competitors
   - Batch processes addresses through Smarty
   - Filters results by acreage

3. **Rate Limiting**: Service includes 100ms delay between requests to respect rate limits.

4. **Error Handling**: All methods handle errors gracefully and log warnings if Smarty is unavailable.

## Testing

Test the Smarty integration:

```python
cd backend
poetry run python -c "
from app.services.smarty_service import SmartyService
import os
from dotenv import load_dotenv
load_dotenv()

smarty = SmartyService()
print(f'Smarty available: {smarty.available}')
if smarty.available:
    result = smarty.geocode_address('123 Main St', 'Lexington', 'KY', '40508')
    print(f'Geocoding result: {result}')
"
```

## Documentation

- Smarty API Docs: https://www.smarty.com/docs
- Cloud API: https://www.smarty.com/docs/cloud
- Property Data API: Check docs for exact endpoint structure

## Next Steps

1. ✅ Service created and integrated
2. ✅ ZoningScraper updated to use Smarty
3. ✅ ParcelService updated to use Smarty
4. ⏳ Test with actual API calls (requires valid credentials)
5. ⏳ Adjust endpoint structure based on actual Smarty API response format

