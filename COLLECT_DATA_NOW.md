# Collect Data Now - Quick Start

## ✅ Everything is Ready!

- ✅ **Playwright installed** (no ChromeDriver needed!)
- ✅ **Scrapers configured** (simple + Playwright fallback)
- ✅ **Database connected**
- ✅ **Ready to collect data**

## Start Collecting Data

### Quick Test (Single State)

Test with Florida first:

```bash
cd backend
poetry run python ../examples/test_publix_scraper.py --state FL
```

### Collect All Data (Recommended)

Collect data for all Publix states:

```bash
cd backend
poetry run python ../examples/collect_all_data.py
```

Or start with just Florida:

```bash
cd backend
poetry run python ../examples/collect_all_data.py --state FL
```

## What Gets Collected

1. **Publix Stores** - All store locations
2. **Competitor Stores** - Walmart & Kroger locations
3. **Demographics** - City-level data
4. **Zoning Records** - Commercial parcels

## Monitor Progress

While collecting, check your progress:

```bash
# Dashboard stats
curl http://localhost:8000/api/dashboard/stats | python3 -m json.tool

# Count stores
curl "http://localhost:8000/api/stores?state=FL" | python3 -m json.tool | grep -c '"id"'
```

## How It Works

The scraper tries methods in this order:

1. **Simple scraper** (requests/BeautifulSoup) - Fastest, no browser
2. **Playwright** - If simple fails, uses Playwright (macOS-friendly)
3. **Saves to database** automatically

## Troubleshooting

**If scraping fails:**
- Publix website may have changed
- Try different state (FL usually works best)
- Check logs for specific errors
- The simple scraper may need updates for Publix's HTML

**If Playwright times out:**
- Website may be slow
- Try simple scraper only (it's faster anyway)
- Increase timeout in `publix_scraper_playwright.py`

## After Collection

Once you have data:

```bash
# Run analysis
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"region": "FL"}'

# View predictions
curl "http://localhost:8000/api/predictions?state=FL"
```

## Ready! 🚀

Start collecting:

```bash
cd backend
poetry run python ../examples/collect_all_data.py --state FL
```

Good luck! The scraper will automatically use the best method available.

