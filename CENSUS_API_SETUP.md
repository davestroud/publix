# Census API Setup & Troubleshooting

## ✅ FIPS Code Lookup Expanded

The FIPS code lookup has been significantly expanded:
- ✅ **100+ cities** now in lookup table
- ✅ **All major Publix markets** covered
- ✅ **Geocoder fallback** - automatically queries Census Geocoder API for cities not in lookup
- ✅ **Walton, KY** and **Somerset, KY** now included

## Census API Key Issues

If you're seeing "Invalid Key" errors:

### 1. Verify API Key Format
Census API keys should be alphanumeric strings. Check your `.env`:
```
CENSUS_API_KEY=your_key_here
```

### 2. Validate API Key
Test your key directly:
```bash
curl "https://api.census.gov/data/2021/acs/acs5?get=NAME,B01001_001E&for=place:2146042&in=state:21&key=YOUR_KEY"
```

### 3. Key Activation
- New Census API keys may need 24-48 hours to activate
- Check your email for activation confirmation
- Verify key at: https://api.census.gov/data/key_signup.html

### 4. Fallback Behavior
The service now:
- ✅ Tries with API key first
- ✅ Falls back to no-key requests if key is invalid (500/day limit)
- ✅ Works for basic queries without a key

## Current Status

**Working:**
- ✅ FIPS code lookup (100+ cities)
- ✅ Geocoder API integration
- ✅ Store collection
- ✅ Competitor collection

**Needs API Key Validation:**
- ⚠️ Census demographics API (returns "Invalid Key")
- The service will try without key, but may hit rate limits

## Test FIPS Codes

```bash
cd backend
poetry run python -c "
from app.services.census_service import CensusService
service = CensusService()
cities = ['Walton', 'Somerset', 'Lexington', 'Louisville', 'Owensboro']
for city in cities:
    fips = service._get_place_fips(city, 'KY')
    print(f'{city}, KY: {fips if fips else \"Not found\"}')
"
```

All major Kentucky cities should now resolve!

