#!/usr/bin/env python3
"""
Simple test to call the SerpApi directly to verify API key works.
"""
import os
from dotenv import load_dotenv
from serpapi import SerpApiClient as SerpApiSearch

# Load environment variables
load_dotenv()
API_KEY = os.getenv("SERPAPI_API_KEY")

def test_direct_serpapi():
    print(f"Testing with API key: {API_KEY[:10]}...")
    
    # Test basic search
    print("\n🔍 Testing basic search...")
    try:
        params = {
            "api_key": API_KEY,
            "engine": "google_light",
            "q": "coffee"
        }
        search = SerpApiSearch(params)
        data = search.get_dict()
        print(f"✅ Search successful! Found {len(data.get('organic_results', []))} results")
    except Exception as e:
        print(f"❌ Search failed: {e}")
        return False
    
    # Test flights search
    print("\n✈️  Testing flights search...")
    try:
        params = {
            "api_key": API_KEY,
            "engine": "google_flights",
            "departure_id": "LAX",
            "arrival_id": "JFK",
            "outbound_date": "2025-08-01",
            "return_date": "2025-08-08",
            "adults": 1,
            "currency": "USD"
        }
        search = SerpApiSearch(params)
        data = search.get_dict()
        
        print(f"Response keys: {list(data.keys())}")
        
        if "best_flights" in data:
            print(f"✅ Found {len(data['best_flights'])} best flights")
        if "other_flights" in data:
            print(f"✅ Found {len(data['other_flights'])} other flights")
        if "error" in data:
            print(f"❌ API Error: {data['error']}")
        if not data.get("best_flights") and not data.get("other_flights"):
            print("❌ No flights found in response")
            print(f"Full response: {data}")
        else:
            print("✅ Flights API working correctly!")
            
    except Exception as e:
        print(f"❌ Flights search failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_direct_serpapi()