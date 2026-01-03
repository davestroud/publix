# Add Google Places API Key

## Step 1: Add API Key to .env

Add this line to `backend/.env`:

```
GOOGLE_PLACES_API_KEY=your_actual_api_key_here
```

**Important:** Replace `your_actual_api_key_here` with your actual Google Places API key.

## Step 2: Verify Setup

Test that it works:

```bash
cd backend
poetry run python ../examples/test_google_places.py --state FL
```

## Step 3: Start Collecting Data

Once verified, collect data:

```bash
cd backend
poetry run python ../examples/collect_all_data.py --state FL
```

## Where to Get API Key

1. Go to: https://console.cloud.google.com/
2. Create/Select a project
3. Enable "Places API"
4. Go to "Credentials" → "Create Credentials" → "API Key"
5. Copy the key and add to `.env`

## Free Tier

- $200/month free credit
- ~$17 per 1,000 requests
- For 1,300 Publix stores: ~$22 (within free tier!)

## Next Steps After Adding Key

1. Test: `poetry run python ../examples/test_google_places.py --state FL`
2. Collect: `poetry run python ../examples/collect_all_data.py --state FL`
3. Analyze: `curl -X POST http://localhost:8000/api/analyze -H "Content-Type: application/json" -d '{"region": "FL"}'`

