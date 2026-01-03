# Quick Test: Direct Publix Scraping

## What's Ready

✅ **Selenium installed** - Already added to dependencies
✅ **Simple scraper** - Uses requests/BeautifulSoup (faster)
✅ **Selenium scraper** - Handles JavaScript-heavy sites
✅ **Auto-fallback** - Tries simple first, falls back to Selenium

## Quick Test (No ChromeDriver Needed)

The simple scraper doesn't need ChromeDriver. Test it:

```bash
cd backend
poetry run python ../examples/test_publix_scraper.py --state KY
```

This will try to scrape Publix stores using just requests/BeautifulSoup.

## Full Test (With ChromeDriver)

If you want to test the Selenium scraper:

1. **Install ChromeDriver:**
   ```bash
   brew install chromedriver
   ```

2. **Test:**
   ```bash
   cd backend
   poetry run python ../examples/test_publix_scraper.py --state KY
   ```

## Use in Your App

The scraper is automatically integrated! Just run:

```bash
# Via data collection script
cd backend
poetry run python ../examples/run_data_collection.py --state KY

# Or via API
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"region": "KY"}'
```

The scraper will:
1. Try simple requests/BeautifulSoup first
2. Fall back to Selenium if needed
3. Extract store data automatically
4. Save to your database

## What Gets Scraped

- Store number (if available)
- Full address
- City, State, Zip
- Latitude/Longitude
- Square footage (if available)

## Next Steps

1. **Test it** - Run the test script above
2. **Check results** - See what data you get
3. **Adjust if needed** - Modify selectors if Publix HTML changed
4. **Add more fields** - Extract hours, phone, etc.

See `DIRECT_SCRAPING_SETUP.md` for full documentation!

