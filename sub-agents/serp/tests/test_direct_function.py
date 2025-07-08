#!/usr/bin/env python3
"""
Test script to test the flights functionality directly.
"""
import asyncio
import os
from dotenv import load_dotenv
from serpapi import SerpApiClient as SerpApiSearch
import httpx

# Load environment variables
load_dotenv()
API_KEY = os.getenv("SERPAPI_API_KEY")

async def test_flights_function_directly():
    """Test the flights function logic directly"""
    print("🧪 Testing flights function logic directly...")
    
    # Test parameters
    params = {
        "departure_id": "LAX",
        "arrival_id": "JFK",
        "outbound_date": "2025-08-01", 
        "return_date": "2025-08-08",
        "adults": 1,
        "currency": "USD"
    }
    
    print(f"📝 Test parameters: {params}")
    
    # Add API key and engine (same as in the actual function)
    params = {
        "api_key": API_KEY,
        "engine": "google_flights",
        **params
    }
    
    try:
        # This mirrors the exact logic from the flights function
        search = SerpApiSearch(params)
        data = search.get_dict()

        if not data:
            result = {"flights": [], "search_metadata": {}, "search_parameters": params, "error": "No response from SerpApi."}
        else:
            # Return the raw best_flights and other_flights arrays as a single list
            flights = []
            if "best_flights" in data and data["best_flights"]:
                flights.extend(data["best_flights"])
            if "other_flights" in data and data["other_flights"]:
                flights.extend(data["other_flights"])

            result = {
                "flights": flights,
                "search_metadata": data.get("search_metadata", {}),
                "search_parameters": data.get("search_parameters", params)
            }
        
        print(f"✅ Function executed successfully!")
        print(f"📊 Response keys: {list(result.keys())}")
        
        if "error" in result:
            print(f"❌ Error in response: {result['error']}")
            return False
            
        flights_data = result.get("flights", [])
        print(f"🛫 Found {len(flights_data)} flights")
        
        if flights_data:
            print("✅ Flights function returns flight data properly!")
            
            # Show sample flight info
            first_flight = flights_data[0]
            if "flights" in first_flight and len(first_flight["flights"]) > 0:
                dep = first_flight["flights"][0]["departure_airport"]
                arr = first_flight["flights"][0]["arrival_airport"]
                print(f"📍 Sample route: {dep['name']} ({dep['id']}) -> {arr['name']} ({arr['id']})")
                print(f"💰 Price: ${first_flight.get('price', 'N/A')}")
                print(f"⏱️  Duration: {first_flight.get('total_duration', 'N/A')} minutes")
            
            # Show metadata
            metadata = result.get("search_metadata", {})
            print(f"🔍 Search ID: {metadata.get('id', 'N/A')}")
            print(f"📈 Status: {metadata.get('status', 'N/A')}")
            
            return True
        else:
            print("❌ No flights found in response")
            print(f"Available data keys: {list(data.keys()) if 'data' in locals() else 'No data'}")
            return False
            
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 429:
            result = {"flights": [], "error": "Error: Rate limit exceeded. Please try again later."}
            print(f"❌ Rate limit error: {result['error']}")
        elif e.response.status_code == 401:
            result = {"flights": [], "error": "Error: Invalid API key. Please check your SERPAPI_API_KEY."}
            print(f"❌ Auth error: {result['error']}")
        else:
            result = {"flights": [], "error": f"Error: {e.response.status_code} - {e.response.text}"}
            print(f"❌ HTTP error: {result['error']}")
        return False
    except Exception as e:
        result = {"flights": [], "error": f"Error: {str(e)}"}
        print(f"❌ Unexpected error: {result['error']}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_flights_function_directly())
    print(f"\n{'✅ TEST PASSED' if success else '❌ TEST FAILED'}")