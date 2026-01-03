#!/bin/bash
# Quick test script for the API endpoints

BASE_URL="http://localhost:8000"

echo "=== Testing Publix Expansion Predictor API ===\n"

echo "1. Dashboard Stats:"
curl -s "$BASE_URL/api/dashboard/stats" | python3 -m json.tool
echo "\n"

echo "2. All Stores:"
curl -s "$BASE_URL/api/stores" | python3 -m json.tool | head -20
echo "\n"

echo "3. Stores in Kentucky:"
curl -s "$BASE_URL/api/stores?state=KY" | python3 -m json.tool
echo "\n"

echo "4. Demographics for Bowling Green:"
curl -s "$BASE_URL/api/demographics/Bowling%20Green?state=KY" | python3 -m json.tool
echo "\n"

echo "5. Zoning Records in Kentucky:"
curl -s "$BASE_URL/api/zoning/KY" | python3 -m json.tool
echo "\n"

echo "✅ API tests complete!"

