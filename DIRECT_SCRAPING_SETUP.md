# Direct Scraping Setup Guide

I've implemented direct scraping for Publix stores. Here's how to use it:

## What Was Implemented

1. **`publix_scraper_simple.py`** - Uses requests/BeautifulSoup (faster, no browser)
2. **`publix_scraper.py`** - Uses Selenium (handles JavaScript-heavy sites)
3. **Updated `scraper.py`** - Automatically tries simple scraper first, falls back to Selenium

## Installation

### 1. Selenium is Already Installed ✅

We already added it: `poetry add selenium`

### 2. Install ChromeDriver

The scraper needs ChromeDriver to control Chrome:

**macOS:**
```bash
brew install chromedriver
```

**Linux:**
```bash
sudo apt-get install chromium-chromedriver
# Or
wget https://chromedriver.storage.googleapis.com/LATEST_RELEASE
# Download and install ChromeDriver
```

**Windows:**
- Download from: https://chromedriver.chromium.org/
- Add to PATH

**Verify installation:**
```bash
chromedriver --version
```

### 3. Alternative: Use ChromeDriver Manager (Automatic)

You can also use `webdriver-manager` to automatically download ChromeDriver:

```bash
cd backend
poetry add webdriver-manager
```

Then update `publix_scraper.py` to use:
```python
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)
```

## How It Works

The scraper tries multiple methods in order:

1. **API Endpoints** - Looks for Publix's internal API
2. **HTML Parsing** - Parses the store locator page HTML
3. **Selenium** - Uses browser automation if needed

## Testing

Test the scraper:

```bash
cd backend
poetry run python ../examples/test_publix_scraper.py --state KY
```

Or test via the data collector:

```bash
cd backend
poetry run python ../examples/run_data_collection.py --state KY
```

## Usage

The scraper is automatically used when you:

1. **Run data collection:**
   ```bash
   poetry run python ../examples/run_data_collection.py --state KY
   ```

2. **Run analysis** (which triggers data collection):
   ```bash
   curl -X POST http://localhost:8000/api/analyze \
     -H "Content-Type: application/json" \
     -d '{"region": "KY"}'
   ```

## Troubleshooting

### "ChromeDriver not found"

Install ChromeDriver (see above) or use webdriver-manager.

### "No stores found"

1. **Check if Publix website changed** - Their HTML structure may have changed
2. **Try different state** - Some states may have different page structures
3. **Check logs** - The scraper logs what it's trying
4. **Use Selenium mode** - Set `headless=False` to see what's happening

### "Selenium timeout"

The website may be slow. Increase wait times in `publix_scraper.py`:
```python
self.driver.implicitly_wait(20)  # Increase from 10
```

### Rate Limiting

Publix may rate limit requests. The scraper includes delays, but you may need to:
- Add more delays between requests
- Use a proxy
- Respect robots.txt

## Customization

### Adjust Scraper Behavior

Edit `backend/app/services/publix_scraper.py`:

- **Headless mode**: Set `headless=False` to see browser
- **Wait times**: Adjust `time.sleep()` values
- **Selectors**: Update CSS selectors if Publix changes their HTML

### Add More Data Extraction

The scraper currently extracts:
- Store number
- Address
- City, State, Zip
- Latitude/Longitude

To add more fields (hours, phone, etc.), update `_parse_store_element()`.

## Legal Considerations

⚠️ **Important**: 
- Check Publix's Terms of Service before scraping
- Respect robots.txt: https://www.publix.com/robots.txt
- Don't overload their servers (use rate limiting)
- Consider contacting Publix for official API access

## Next Steps

1. **Test the scraper** with your target state
2. **Verify data quality** - Check if stores are accurate
3. **Add error handling** - Handle edge cases
4. **Implement caching** - Avoid re-scraping same data
5. **Add more fields** - Extract hours, phone numbers, etc.

## Example Output

When working, you should see:
```
INFO: Found 45 Publix stores
✅ Successfully scraped 45 stores using direct scraper
```

The stores will be automatically saved to your database!

