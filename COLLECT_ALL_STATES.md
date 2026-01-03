# Collecting Data from All Publix States

## Overview

Collecting comprehensive data from all 8 states where Publix operates:
- **Florida (FL)**: ~899 stores (primary market)
- **Georgia (GA)**: ~220 stores
- **Alabama (AL)**: ~96 stores
- **South Carolina (SC)**: ~70 stores
- **Tennessee (TN)**: ~59 stores
- **North Carolina (NC)**: ~58 stores
- **Virginia (VA)**: ~24 stores
- **Kentucky (KY)**: ~4 stores (newer market)

**Total**: ~1,467 Publix locations across 527 cities

## What's Being Collected

### 1. Publix Stores
- Store locations, addresses, coordinates
- Store numbers and metadata
- Uploaded to S3: `scraped-data/publix_stores_{STATE}_{timestamp}.json`

### 2. Competitor Stores
- **Walmart**: Major competitor locations
- **Kroger**: Grocery competitor
- **Chick-fil-A**: Co-location indicator
- **Target**: Retail anchor
- **Costco**: Warehouse competitor

### 3. Demographics
- Population, median income, median age
- Household size, growth rates
- Metro area codes
- Collected for all cities with Publix stores + major cities

### 4. Zoning Records
- Commercial parcels (15-25 acres)
- Zoning codes and status
- Impact fees
- Planning commission records

## Collection Status

The collection script is running in the background. Monitor progress:

```bash
# View live progress
tail -f /tmp/publix_collection.log

# Check current stats
cd backend
poetry run python -c "
from app.services.database import SessionLocal
from app.models.schemas import PublixStore, CompetitorStore, Demographics
db = SessionLocal()
print(f'Publix Stores: {db.query(PublixStore).count()}')
print(f'Competitor Stores: {db.query(CompetitorStore).count()}')
print(f'Demographics Records: {db.query(Demographics).count()}')
db.close()
"
```

## Expected Timeline

- **Publix Stores**: ~30-60 minutes (Google Places API)
- **Competitor Stores**: ~60-90 minutes (multiple APIs)
- **Demographics**: ~20-30 minutes (Census API)
- **Zoning Records**: Varies (depends on availability)

**Total Estimated Time**: 2-3 hours for all states

## After Collection

Once complete, verify data:

```bash
# Dashboard stats
curl http://localhost:8000/api/dashboard/stats | python3 -m json.tool

# Stores by state
curl "http://localhost:8000/api/stores?state=FL" | python3 -m json.tool | head -50

# Run analysis
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"region": "FL"}'
```

## Data Storage

- **Database**: PostgreSQL (AWS RDS)
- **Raw Data**: S3 bucket `publix-expansion-data`
  - `scraped-data/`: Raw scraped store data
  - `data/`: Processed data
  - `reports/`: Analysis reports
  - `cache/`: Cached API responses

## Troubleshooting

If collection stops or errors occur:

1. **Check logs**: `tail -100 /tmp/publix_collection.log`
2. **Verify API keys**: Ensure Google Places and Census API keys are valid
3. **Check database connection**: Verify RDS is accessible
4. **Resume collection**: Run script again (duplicates are skipped)

```bash
# Resume for specific states
cd backend
poetry run python ../examples/collect_all_data.py --states FL GA AL
```

