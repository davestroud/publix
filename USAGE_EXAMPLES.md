# Usage Examples

This guide shows practical examples of how to use the Publix Expansion Predictor application.

## Table of Contents

1. [Quick Start](#quick-start)
2. [API Examples](#api-examples)
3. [Use Cases](#use-cases)
4. [Python Client Examples](#python-client-examples)
5. [Frontend Usage](#frontend-usage)

---

## Quick Start

### Start the Backend

```bash
cd backend
poetry run uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### Interactive API Documentation

Visit **http://localhost:8000/docs** for interactive API documentation where you can:
- See all available endpoints
- Test API calls directly in your browser
- View request/response schemas
- See example requests

---

## API Examples

### 1. Get Dashboard Statistics

**Use Case**: Get an overview of all data in the system

```bash
curl http://localhost:8000/api/dashboard/stats
```

**Response**:
```json
{
  "total_stores": 45,
  "total_predictions": 12,
  "average_confidence": 0.78,
  "recent_predictions": [
    {
      "id": 1,
      "city": "Lexington",
      "state": "KY",
      "confidence_score": 0.85,
      "reasoning": "Strong demographic match with existing Publix markets...",
      "key_factors": {
        "population_growth": "high",
        "competitor_presence": "moderate",
        "zoning_opportunities": 3
      }
    }
  ]
}
```

---

### 2. Get All Publix Stores

**Use Case**: View all existing Publix store locations

```bash
# Get all stores
curl http://localhost:8000/api/stores

# Filter by state
curl "http://localhost:8000/api/stores?state=KY"

# Filter by city
curl "http://localhost:8000/api/stores?city=Lexington&state=KY"

# Limit results
curl "http://localhost:8000/api/stores?limit=10"
```

**Response**:
```json
[
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
]
```

---

### 3. Get Predictions

**Use Case**: View predicted new store locations

```bash
# Get all predictions
curl http://localhost:8000/api/predictions

# Filter by state
curl "http://localhost:8000/api/predictions?state=KY"

# Filter by minimum confidence score
curl "http://localhost:8000/api/predictions?min_confidence=0.8"

# Combine filters
curl "http://localhost:8000/api/predictions?state=KY&min_confidence=0.75&limit=5"
```

**Response**:
```json
[
  {
    "id": 1,
    "city": "Bowling Green",
    "state": "KY",
    "latitude": 36.9685,
    "longitude": -86.4808,
    "confidence_score": 0.87,
    "reasoning": "Bowling Green shows strong expansion potential due to...",
    "predicted_store_size": 50000,
    "key_factors": {
      "demographics": "favorable",
      "competition": "moderate",
      "zoning": "available"
    },
    "created_at": "2024-01-15T10:30:00"
  }
]
```

---

### 4. Run Regional Analysis

**Use Case**: Analyze an entire state or region for expansion opportunities

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "region": "KY"
  }'
```

**With Specific Cities**:
```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "region": "KY",
    "cities": [
      {"city": "Lexington", "state": "KY"},
      {"city": "Bowling Green", "state": "KY"},
      {"city": "Owensboro", "state": "KY"}
    ]
  }'
```

**Response**:
```json
{
  "analysis_run_id": 1,
  "status": "completed",
  "predictions": [
    {
      "id": 1,
      "city": "Bowling Green",
      "state": "KY",
      "confidence_score": 0.87,
      "reasoning": "...",
      "key_factors": {...}
    }
  ],
  "report": {
    "summary": "Analysis of Kentucky identified 5 high-potential locations...",
    "key_findings": [
      "Strong expansion opportunity in Bowling Green",
      "Moderate potential in Owensboro"
    ],
    "recommendations": [
      "Focus on secondary cities with population 50k-100k",
      "Consider proximity to existing stores"
    ]
  },
  "analysis_data": {
    "stores_analyzed": 12,
    "competitors_found": 45,
    "zoning_records_reviewed": 23
  }
}
```

**Note**: This endpoint triggers the multi-agent system which:
1. Collects data (stores, competitors, demographics, zoning)
2. Analyzes patterns
3. Evaluates sites
4. Generates predictions and reports

This may take 1-2 minutes to complete.

---

### 5. Analyze a Single City

**Use Case**: Get detailed analysis for a specific city

```bash
curl -X POST http://localhost:8000/api/analyze/city \
  -H "Content-Type: application/json" \
  -d '{
    "city": "Bowling Green",
    "state": "KY"
  }'
```

**Response**:
```json
{
  "city": "Bowling Green",
  "state": "KY",
  "analysis": {
    "demographics": {
      "population": 72000,
      "median_income": 45000,
      "growth_rate": 0.025
    },
    "existing_stores": 0,
    "competitors": [
      {"name": "Walmart", "count": 2},
      {"name": "Kroger", "count": 1}
    ],
    "zoning_opportunities": 3,
    "confidence_score": 0.87,
    "recommendation": "High potential - strong demographics and available zoning"
  }
}
```

---

### 6. Get Demographic Data

**Use Case**: View demographic information for a city

```bash
curl "http://localhost:8000/api/demographics/Bowling%20Green?state=KY"
```

**Response**:
```json
{
  "id": 1,
  "city": "Bowling Green",
  "state": "KY",
  "population": 72000,
  "median_income": 45000.0,
  "growth_rate": 0.025,
  "median_age": 32.5,
  "household_size": 2.4,
  "data_year": 2023
}
```

---

### 7. Get Zoning Records

**Use Case**: Find available commercial parcels suitable for development

```bash
# Get all zoning records for a state
curl "http://localhost:8000/api/zoning/KY"

# Filter by city
curl "http://localhost:8000/api/zoning/KY?city=Bowling%20Green"

# Filter by acreage (15-25 acres ideal for Publix)
curl "http://localhost:8000/api/zoning/KY?min_acreage=15&max_acreage=25"

# Combined filters
curl "http://localhost:8000/api/zoning/KY?city=Bowling%20Green&min_acreage=15&max_acreage=25"
```

**Response**:
```json
[
  {
    "id": 1,
    "parcel_id": "KY-2024-001",
    "address": "1234 Scottsville Rd",
    "city": "Bowling Green",
    "state": "KY",
    "latitude": 36.9685,
    "longitude": -86.4808,
    "acreage": 18.5,
    "zoning_status": "pending",
    "permit_type": "commercial",
    "description": "Commercial rezoning request for retail development",
    "record_date": "2024-01-10T00:00:00"
  }
]
```

---

## Use Cases

### Use Case 1: Identify Expansion Opportunities in a New State

**Scenario**: Publix wants to expand into Kentucky

```bash
# Step 1: Run analysis for the entire state
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"region": "KY"}' > ky_analysis.json

# Step 2: Get top predictions
curl "http://localhost:8000/api/predictions?state=KY&min_confidence=0.8" | jq '.[] | {city, confidence_score, reasoning}'

# Step 3: Get detailed zoning opportunities
curl "http://localhost:8000/api/zoning/KY?min_acreage=15&max_acreage=25" | jq '.[] | {city, address, acreage, zoning_status}'
```

---

### Use Case 2: Evaluate Specific Cities

**Scenario**: Compare multiple cities for expansion

```bash
# Analyze multiple cities
for city in "Lexington" "Bowling Green" "Owensboro"; do
  echo "Analyzing $city..."
  curl -X POST http://localhost:8000/api/analyze/city \
    -H "Content-Type: application/json" \
    -d "{\"city\": \"$city\", \"state\": \"KY\"}" \
    | jq '{city, confidence_score, recommendation}'
done
```

---

### Use Case 3: Monitor Dashboard Metrics

**Scenario**: Track overall system statistics

```bash
# Get dashboard stats
curl http://localhost:8000/api/dashboard/stats | jq '{
  total_stores,
  total_predictions,
  average_confidence,
  top_cities: .recent_predictions[] | {city, state, confidence_score}
}'
```

---

### Use Case 4: Find Suitable Parcels

**Scenario**: Find 15-25 acre parcels in specific cities

```bash
# Find suitable parcels in Kentucky cities
curl "http://localhost:8000/api/zoning/KY?min_acreage=15&max_acreage=25" \
  | jq 'group_by(.city) | .[] | {
    city: .[0].city,
    parcels: length,
    total_acreage: (map(.acreage) | add),
    addresses: [.[].address]
  }'
```

---

## Python Client Examples

### Example 1: Basic Client Class

```python
import requests
from typing import List, Dict, Optional

class PublixExpansionClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def get_dashboard_stats(self) -> Dict:
        """Get dashboard statistics"""
        response = self.session.get(f"{self.base_url}/api/dashboard/stats")
        response.raise_for_status()
        return response.json()
    
    def get_stores(self, state: Optional[str] = None, city: Optional[str] = None) -> List[Dict]:
        """Get Publix stores"""
        params = {}
        if state:
            params["state"] = state
        if city:
            params["city"] = city
        
        response = self.session.get(f"{self.base_url}/api/stores", params=params)
        response.raise_for_status()
        return response.json()
    
    def get_predictions(self, state: Optional[str] = None, min_confidence: Optional[float] = None) -> List[Dict]:
        """Get predictions"""
        params = {}
        if state:
            params["state"] = state
        if min_confidence:
            params["min_confidence"] = min_confidence
        
        response = self.session.get(f"{self.base_url}/api/predictions", params=params)
        response.raise_for_status()
        return response.json()
    
    def analyze_region(self, region: str, cities: Optional[List[Dict]] = None) -> Dict:
        """Run analysis for a region"""
        payload = {"region": region}
        if cities:
            payload["cities"] = cities
        
        response = self.session.post(f"{self.base_url}/api/analyze", json=payload)
        response.raise_for_status()
        return response.json()
    
    def analyze_city(self, city: str, state: str) -> Dict:
        """Analyze a single city"""
        payload = {"city": city, "state": state}
        response = self.session.post(f"{self.base_url}/api/analyze/city", json=payload)
        response.raise_for_status()
        return response.json()
    
    def get_demographics(self, city: str, state: str) -> Dict:
        """Get demographic data"""
        response = self.session.get(
            f"{self.base_url}/api/demographics/{city}",
            params={"state": state}
        )
        response.raise_for_status()
        return response.json()
    
    def get_zoning_records(self, region: str, min_acreage: float = 15.0, max_acreage: float = 25.0) -> List[Dict]:
        """Get zoning records"""
        params = {"min_acreage": min_acreage, "max_acreage": max_acreage}
        response = self.session.get(f"{self.base_url}/api/zoning/{region}", params=params)
        response.raise_for_status()
        return response.json()


# Usage examples
if __name__ == "__main__":
    client = PublixExpansionClient()
    
    # Get dashboard stats
    stats = client.get_dashboard_stats()
    print(f"Total stores: {stats['total_stores']}")
    print(f"Total predictions: {stats['total_predictions']}")
    
    # Get stores in Kentucky
    stores = client.get_stores(state="KY")
    print(f"\nFound {len(stores)} stores in Kentucky")
    
    # Get high-confidence predictions
    predictions = client.get_predictions(state="KY", min_confidence=0.8)
    print(f"\nFound {len(predictions)} high-confidence predictions")
    for pred in predictions:
        print(f"  - {pred['city']}, {pred['state']}: {pred['confidence_score']:.2%}")
    
    # Analyze a city
    analysis = client.analyze_city("Bowling Green", "KY")
    print(f"\nAnalysis for Bowling Green, KY:")
    print(f"  Confidence: {analysis['analysis']['confidence_score']:.2%}")
    print(f"  Recommendation: {analysis['analysis']['recommendation']}")
    
    # Get zoning opportunities
    zoning = client.get_zoning_records("KY", min_acreage=15, max_acreage=25)
    print(f"\nFound {len(zoning)} suitable parcels")
```

---

### Example 2: Batch Analysis Script

```python
from publix_client import PublixExpansionClient
import json

def analyze_multiple_cities(client: PublixExpansionClient, cities: List[tuple]):
    """Analyze multiple cities and compare results"""
    results = []
    
    for city, state in cities:
        print(f"Analyzing {city}, {state}...")
        try:
            analysis = client.analyze_city(city, state)
            results.append({
                "city": city,
                "state": state,
                "confidence": analysis["analysis"]["confidence_score"],
                "recommendation": analysis["analysis"]["recommendation"]
            })
        except Exception as e:
            print(f"Error analyzing {city}: {e}")
    
    # Sort by confidence
    results.sort(key=lambda x: x["confidence"], reverse=True)
    
    return results

# Usage
client = PublixExpansionClient()
cities_to_analyze = [
    ("Lexington", "KY"),
    ("Bowling Green", "KY"),
    ("Owensboro", "KY"),
    ("Paducah", "KY")
]

results = analyze_multiple_cities(client, cities_to_analyze)

print("\n=== Analysis Results ===")
for result in results:
    print(f"{result['city']}, {result['state']}: {result['confidence']:.2%}")
    print(f"  {result['recommendation']}\n")
```

---

### Example 3: Export Data to CSV

```python
import csv
from publix_client import PublixExpansionClient

def export_predictions_to_csv(client: PublixExpansionClient, filename: str = "predictions.csv"):
    """Export predictions to CSV"""
    predictions = client.get_predictions()
    
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['city', 'state', 'confidence_score', 'latitude', 'longitude', 'reasoning']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for pred in predictions:
            writer.writerow({
                'city': pred['city'],
                'state': pred['state'],
                'confidence_score': pred['confidence_score'],
                'latitude': pred.get('latitude', ''),
                'longitude': pred.get('longitude', ''),
                'reasoning': pred['reasoning'][:100]  # Truncate long text
            })
    
    print(f"Exported {len(predictions)} predictions to {filename}")

# Usage
client = PublixExpansionClient()
export_predictions_to_csv(client)
```

---

## Frontend Usage

### Starting the Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:3000`

### Frontend Features

1. **Dashboard Tab**: View overall statistics and metrics
2. **Map Tab**: Interactive map showing stores and predictions
3. **Data Table Tab**: Sortable, filterable table with CSV export
4. **Reports Tab**: View and generate analysis reports

### Using the Frontend

1. **View Dashboard**: Click "Dashboard" tab to see:
   - Total stores count
   - Total predictions
   - Average confidence score
   - Recent predictions

2. **Explore Map**: Click "Map" tab to:
   - See all Publix stores (blue markers)
   - See predictions (red markers with confidence scores)
   - Click markers for details
   - Filter by state/city

3. **Browse Data**: Click "Data Table" tab to:
   - View all stores or predictions
   - Sort by any column
   - Filter by state, city, confidence score
   - Export to CSV

4. **Run Analysis**: Click "Reports" tab to:
   - Select a region (state)
   - Click "Run Analysis"
   - View generated predictions and report
   - See LLM-generated insights

---

## Advanced Examples

### Example: Complete Expansion Analysis Workflow

```python
from publix_client import PublixExpansionClient
import json

def complete_expansion_analysis(client: PublixExpansionClient, state: str):
    """Complete workflow for expansion analysis"""
    
    print(f"=== Analyzing {state} for Publix Expansion ===\n")
    
    # Step 1: Get current stores
    print("Step 1: Getting existing stores...")
    stores = client.get_stores(state=state)
    print(f"Found {len(stores)} existing stores\n")
    
    # Step 2: Run regional analysis
    print("Step 2: Running regional analysis...")
    analysis = client.analyze_region(state)
    print(f"Analysis completed: {analysis['status']}\n")
    
    # Step 3: Get top predictions
    print("Step 3: Getting top predictions...")
    predictions = client.get_predictions(state=state, min_confidence=0.7)
    print(f"Found {len(predictions)} predictions\n")
    
    # Step 4: Get zoning opportunities
    print("Step 4: Finding zoning opportunities...")
    zoning = client.get_zoning_records(state, min_acreage=15, max_acreage=25)
    print(f"Found {len(zoning)} suitable parcels\n")
    
    # Step 5: Generate report
    print("=== Analysis Summary ===")
    print(f"Existing Stores: {len(stores)}")
    print(f"Predictions: {len(predictions)}")
    print(f"Zoning Opportunities: {len(zoning)}")
    
    print("\n=== Top 5 Predictions ===")
    for i, pred in enumerate(predictions[:5], 1):
        print(f"{i}. {pred['city']}, {pred['state']}: {pred['confidence_score']:.2%}")
        print(f"   {pred['reasoning'][:100]}...")
    
    # Save results
    results = {
        "state": state,
        "stores": stores,
        "predictions": predictions,
        "zoning": zoning,
        "analysis": analysis
    }
    
    with open(f"{state}_analysis.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\nResults saved to {state}_analysis.json")

# Usage
client = PublixExpansionClient()
complete_expansion_analysis(client, "KY")
```

---

## Tips and Best Practices

1. **Use Interactive Docs**: Visit `http://localhost:8000/docs` for the easiest way to test endpoints

2. **Filter Results**: Always use filters (state, city, min_confidence) to get relevant data

3. **Batch Operations**: For multiple cities, use the batch analysis endpoint rather than individual calls

4. **Monitor Dashboard**: Check dashboard stats regularly to track system health

5. **Export Data**: Use CSV export for further analysis in Excel/Python/R

6. **Error Handling**: Always check response status codes and handle errors gracefully

7. **Rate Limiting**: Be mindful of API rate limits when running multiple analyses

---

## Need Help?

- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Setup Guide**: See `SETUP.md`
- **Environment Variables**: See `ENV_SETUP.md`

