# API Quick Reference

## Base URL
```
http://localhost:8000
```

## Interactive Documentation
```
http://localhost:8000/docs
```

---

## Endpoints

### Dashboard

**GET** `/api/dashboard/stats`
- Get overall statistics
- **Response**: `{total_stores, total_predictions, average_confidence, recent_predictions}`

---

### Stores

**GET** `/api/stores`
- Get Publix store locations
- **Query Parameters**:
  - `state` (optional): Filter by state code
  - `city` (optional): Filter by city name
  - `limit` (default: 100): Max results (1-1000)
- **Example**: `/api/stores?state=KY&city=Lexington`

---

### Predictions

**GET** `/api/predictions`
- Get predicted new store locations
- **Query Parameters**:
  - `state` (optional): Filter by state
  - `city` (optional): Filter by city
  - `min_confidence` (optional): Minimum confidence (0.0-1.0)
  - `limit` (default: 100): Max results
- **Example**: `/api/predictions?state=KY&min_confidence=0.8`

---

### Analysis

**POST** `/api/analyze`
- Run analysis for a region
- **Body**:
  ```json
  {
    "region": "KY",
    "cities": [{"city": "Lexington", "state": "KY"}]  // optional
  }
  ```
- **Response**: `{analysis_run_id, status, predictions, report, analysis_data}`

**POST** `/api/analyze/city`
- Analyze a single city
- **Body**:
  ```json
  {
    "city": "Bowling Green",
    "state": "KY"
  }
  ```

---

### Demographics

**GET** `/api/demographics/{city}`
- Get demographic data for a city
- **Query Parameters**:
  - `state` (required): State code
- **Example**: `/api/demographics/Bowling%20Green?state=KY`

---

### Zoning

**GET** `/api/zoning/{region}`
- Get zoning records
- **Query Parameters**:
  - `city` (optional): Filter by city
  - `min_acreage` (default: 15.0): Minimum acreage
  - `max_acreage` (default: 25.0): Maximum acreage
  - `limit` (default: 100): Max results
- **Example**: `/api/zoning/KY?min_acreage=15&max_acreage=25`

---

## Common Use Cases

### 1. Get all stores in a state
```bash
curl "http://localhost:8000/api/stores?state=KY"
```

### 2. Get top predictions
```bash
curl "http://localhost:8000/api/predictions?min_confidence=0.8&limit=10"
```

### 3. Run regional analysis
```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"region": "KY"}'
```

### 4. Analyze a city
```bash
curl -X POST http://localhost:8000/api/analyze/city \
  -H "Content-Type: application/json" \
  -d '{"city": "Bowling Green", "state": "KY"}'
```

### 5. Find suitable parcels
```bash
curl "http://localhost:8000/api/zoning/KY?min_acreage=15&max_acreage=25"
```

---

## Python Client

```python
from examples.publix_client import PublixExpansionClient

client = PublixExpansionClient()

# Get stats
stats = client.get_dashboard_stats()

# Get stores
stores = client.get_stores(state="KY")

# Get predictions
predictions = client.get_predictions(state="KY", min_confidence=0.8)

# Run analysis
analysis = client.analyze_region("KY")

# Analyze city
city_analysis = client.analyze_city("Bowling Green", "KY")
```

---

## Response Formats

### Store Response
```json
{
  "id": 1,
  "store_number": "1234",
  "address": "123 Main St",
  "city": "Lexington",
  "state": "KY",
  "zip_code": "40502",
  "latitude": 38.0406,
  "longitude": -84.5037,
  "square_feet": 45000,
  "opening_date": "2020-03-15T00:00:00"
}
```

### Prediction Response
```json
{
  "id": 1,
  "city": "Bowling Green",
  "state": "KY",
  "latitude": 36.9685,
  "longitude": -86.4808,
  "confidence_score": 0.87,
  "reasoning": "Strong expansion potential...",
  "predicted_store_size": 50000,
  "key_factors": {...},
  "created_at": "2024-01-15T10:30:00"
}
```

---

## Status Codes

- `200` - Success
- `400` - Bad Request (invalid parameters)
- `404` - Not Found
- `500` - Internal Server Error

---

## Tips

1. **Use Interactive Docs**: Visit `/docs` for easiest testing
2. **Filter Results**: Always use query parameters to narrow results
3. **Check Health**: Use `/health` endpoint to verify server status
4. **Batch Operations**: Use regional analysis for multiple cities
5. **Export Data**: Use CSV export in frontend or Python client

---

For detailed examples, see `USAGE_EXAMPLES.md`

