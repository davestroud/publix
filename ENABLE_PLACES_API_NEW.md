# Enable Places API (New) in Google Cloud Console

## The Issue

Google deprecated the legacy Places API. You need to enable the **Places API (New)**.

## Steps to Fix

### 1. Go to Google Cloud Console
https://console.cloud.google.com/

### 2. Select Your Project
Make sure you're in the project that has your API key.

### 3. Enable Places API (New)
1. Go to **APIs & Services** → **Library**
2. Search for **"Places API (New)"**
3. Click on it
4. Click **"Enable"**

### 4. Verify Billing
- The Places API (New) requires billing to be enabled
- Don't worry - you get $200/month free credit
- For 1,300 stores: ~$22 (well within free tier)

### 5. Test Again

```bash
cd backend
poetry run python ../examples/test_google_places.py --state FL
```

## What Changed

The scraper now uses:
- **New API endpoint**: `https://places.googleapis.com/v1/places:searchText`
- **New request format**: JSON payload with headers
- **New response format**: Different structure

The code has been updated to use the new API automatically.

## Alternative: Use Legacy API

If you prefer to use the legacy API:
1. Enable **"Places API"** (without "New")
2. But Google recommends using the new API

## After Enabling

Once enabled, the scraper will work automatically. No code changes needed!

