# Complete Data Collection Guide

Now that ChromeDriver is installed, here's how to collect as much data as possible!

## Quick Start

### Option 1: Collect Data for All Publix States (Recommended)

This will collect data for all 8 states where Publix operates:

```bash
cd backend
poetry run python ../examples/collect_all_data.py
```

**This will collect:**
- ✅ Publix stores (all states)
- ✅ Competitor stores (Walmart, Kroger)
- ✅ Demographics (major cities)
- ✅ Zoning records (commercial parcels)

**Time**: ~30-60 minutes (depending on scraping speed)

### Option 2: Collect Data for Specific States

```bash
# Single state
cd backend
poetry run python ../examples/collect_all_data.py --state FL

# Multiple states
poetry run python ../examples/collect_all_data.py --states FL GA AL SC
```

### Option 3: Test First (Single State)

Test with one state first:

```bash
cd backend
poetry run python ../examples/test_publix_scraper.py --state FL
```

## What Gets Collected

### 1. Publix Stores
- Store locations from Publix website
- Address, city, state, zip
- Coordinates (latitude/longitude)
- Store numbers (if available)

**States**: FL, GA, AL, SC, NC, TN, VA, KY

### 2. Competitor Stores
- Walmart locations
- Kroger locations
- Used to identify market opportunities

### 3. Demographics
- Population
- Median income
- Growth rate
- Median age
- Household size

**Cities**: Major cities in each state (top 20 per state)

### 4. Zoning Records
- Commercial parcels
- 15-25 acre parcels (ideal for Publix)
- Zoning status (pending/approved)
- Permit types

## Monitor Progress

While collecting, you can check progress:

```bash
# Check dashboard stats
curl http://localhost:8000/api/dashboard/stats

# Check stores by state
curl "http://localhost:8000/api/stores?state=FL"

# Count stores in database
cd backend
poetry run python -c "from app.services.database import SessionLocal; from app.models.schemas import PublixStore; db = SessionLocal(); print(f'Total stores: {db.query(PublixStore).count()}'); db.close()"
```

## Expected Results

After running collection for all states, you should have:

- **Publix Stores**: ~1,300+ stores (Publix has ~1,300 stores total)
- **Competitor Stores**: ~5,000+ stores (Walmart + Kroger)
- **Demographics**: ~100-150 city records
- **Zoning Records**: Varies by state (depends on available data)

## Troubleshooting

### "ChromeDriver not found"
```bash
# Verify installation
chromedriver --version

# If not found, install:
brew install chromedriver  # macOS
```

### "No stores found"
- Publix website structure may have changed
- Check logs for specific errors
- Try a different state (FL usually has most stores)
- The scraper may need updates for Publix's current HTML

### "Rate limiting / Timeout"
- The scraper includes delays, but Publix may still rate limit
- Try collecting one state at a time
- Add more delays if needed

### "Demographics not found"
- Census API may need API key
- Some cities may not have data available
- This is expected - demographics service needs implementation

### "Zoning records not found"
- Zoning scraper needs implementation
- Each city has different zoning websites
- This is expected - zoning scraper is a placeholder

## After Collection

### 1. Verify Data

```bash
# Get dashboard stats
curl http://localhost:8000/api/dashboard/stats | python3 -m json.tool

# Get stores by state
curl "http://localhost:8000/api/stores?state=FL" | python3 -m json.tool | head -50
```

### 2. Run Analysis

Once you have data, run analysis:

```bash
# Analyze a state
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"region": "FL"}'
```

### 3. View Results

```bash
# Get predictions
curl "http://localhost:8000/api/predictions?state=FL&min_confidence=0.7"

# Get dashboard
curl http://localhost:8000/api/dashboard/stats
```

## Tips for Maximum Data Collection

1. **Start with FL** - Florida has the most Publix stores (~800+)
2. **Run during off-peak hours** - Less likely to hit rate limits
3. **Monitor progress** - Check dashboard stats periodically
4. **Save frequently** - Data is saved to database as it's collected
5. **Handle errors gracefully** - Script continues even if one state fails

## Next Steps After Collection

1. **Run analyses** for each state
2. **Generate predictions** using the multi-agent system
3. **View reports** with LLM-generated insights
4. **Export data** for further analysis

## Example: Full Workflow

```bash
# 1. Collect all data
cd backend
poetry run python ../examples/collect_all_data.py

# 2. Check what we got
curl http://localhost:8000/api/dashboard/stats

# 3. Run analysis for Florida
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"region": "FL"}'

# 4. View predictions
curl "http://localhost:8000/api/predictions?state=FL&min_confidence=0.8"
```

## Need Help?

- Check logs: The script logs progress and errors
- Test individual components: Use `test_publix_scraper.py` first
- Start small: Test with one state before collecting all
- Check database: Verify data is being saved

Good luck collecting data! 🚀

