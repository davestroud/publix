# Start Collecting Data - Quick Guide

## ✅ Setup Complete!

- ✅ Playwright installed (no ChromeDriver needed!)
- ✅ Scrapers ready
- ✅ Database connected
- ✅ Everything configured

## Quick Start: Collect Data

### Option 1: Collect All Publix States (Recommended)

This collects data for all 8 states where Publix operates:

```bash
cd backend
poetry run python ../examples/collect_all_data.py
```

**What it collects:**
- Publix stores (all states)
- Competitor stores (Walmart, Kroger)  
- Demographics (major cities)
- Zoning records (commercial parcels)

**Time**: ~30-60 minutes

### Option 2: Start with One State (Faster Test)

Test with Florida first (most Publix stores):

```bash
cd backend
poetry run python ../examples/collect_all_data.py --state FL
```

### Option 3: Test Scraper First

Make sure scraping works:

```bash
cd backend
poetry run python ../examples/test_publix_scraper.py --state FL
```

## Monitor Progress

While collecting, check progress:

```bash
# Dashboard stats
curl http://localhost:8000/api/dashboard/stats

# Stores by state
curl "http://localhost:8000/api/stores?state=FL" | python3 -m json.tool | head -30
```

## What Happens

The scraper will:

1. **Try simple scraper first** (requests/BeautifulSoup - fastest, no browser)
2. **Fall back to Playwright** if needed (handles JavaScript, macOS-friendly)
3. **Extract store data** automatically
4. **Save to database** as it collects

## Expected Results

After collecting all states, you should have:

- **~1,300+ Publix stores** (Publix has ~1,300 total)
- **~5,000+ competitor stores** (Walmart + Kroger)
- **~100-150 demographic records** (major cities)
- **Zoning records** (varies by state)

## After Collection

### 1. Verify Data

```bash
curl http://localhost:8000/api/dashboard/stats | python3 -m json.tool
```

### 2. Run Analysis

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"region": "FL"}'
```

### 3. View Predictions

```bash
curl "http://localhost:8000/api/predictions?state=FL&min_confidence=0.7"
```

## Troubleshooting

**"No stores found"**
- Publix website may have changed
- Check logs for specific errors
- Try different state (FL usually works best)

**"Playwright browser not found"**
```bash
poetry run playwright install chromium
```

**"Rate limiting"**
- Add delays between requests
- Collect one state at a time
- Run during off-peak hours

## Ready to Go! 🚀

Start collecting:

```bash
cd backend
poetry run python ../examples/collect_all_data.py --state FL
```

Then check your results and run analyses!

