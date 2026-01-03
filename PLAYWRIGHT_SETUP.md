# Playwright Setup (Recommended Alternative to ChromeDriver)

Since ChromeDriver isn't recommended on macOS, we're using **Playwright** instead. Playwright is better because:

✅ **No manual browser driver installation** - Handles it automatically
✅ **Better macOS support** - Works seamlessly on Apple Silicon
✅ **More reliable** - Better handling of modern web apps
✅ **Multiple browsers** - Supports Chromium, Firefox, WebKit
✅ **Apple-friendly** - No security warnings

## Installation

### 1. Install Playwright Package

```bash
cd backend
poetry add playwright
```

### 2. Install Browser Binaries

Playwright will download browsers automatically:

```bash
poetry run playwright install
```

Or install just Chromium:

```bash
poetry run playwright install chromium
```

**Note**: First run will download ~200MB of browser binaries. This is a one-time download.

## How It Works

The scraper now uses this priority order:

1. **Simple scraper** (requests/BeautifulSoup) - Fastest, no browser
2. **Playwright** - If simple scraper fails, uses Playwright
3. **Selenium** - Only as last resort (not recommended)

## Usage

Everything works the same! Just run:

```bash
# Test scraper
cd backend
poetry run python ../examples/test_publix_scraper.py --state FL

# Collect all data
poetry run python ../examples/collect_all_data.py
```

## Advantages Over Selenium/ChromeDriver

| Feature | Playwright | Selenium/ChromeDriver |
|---------|-----------|----------------------|
| Browser Installation | Automatic | Manual (ChromeDriver) |
| macOS Support | Excellent | Security warnings |
| Apple Silicon | Native support | May need Rosetta |
| Reliability | Better | Good |
| Speed | Faster | Slower |
| Setup | `playwright install` | Multiple steps |

## Troubleshooting

### "Playwright not installed"

```bash
cd backend
poetry add playwright
poetry run playwright install
```

### "Browser not found"

```bash
poetry run playwright install chromium
```

### "Permission denied" (macOS)

Playwright browsers are signed and shouldn't have permission issues. If you do:

```bash
# Allow in System Preferences > Security & Privacy
# Or run:
xattr -d com.apple.quarantine ~/.cache/ms-playwright/chromium-*/chrome-mac/Chromium.app
```

## Removing Selenium (Optional)

If you want to remove Selenium entirely:

```bash
cd backend
poetry remove selenium
```

The code will automatically use Playwright instead.

## Browser Options

Playwright supports multiple browsers. To use a different one, edit `publix_scraper_playwright.py`:

```python
# Use Firefox instead of Chromium
self.browser = self.playwright.firefox.launch(headless=self.headless)

# Or WebKit (Safari engine)
self.browser = self.playwright.webkit.launch(headless=self.headless)
```

## Performance

Playwright is typically:
- **2-3x faster** than Selenium
- **More reliable** with modern JavaScript-heavy sites
- **Better at waiting** for dynamic content

## Next Steps

1. **Install Playwright**: `poetry add playwright && poetry run playwright install`
2. **Test**: `poetry run python ../examples/test_publix_scraper.py --state FL`
3. **Collect data**: `poetry run python ../examples/collect_all_data.py`

That's it! Playwright handles everything automatically. 🚀

