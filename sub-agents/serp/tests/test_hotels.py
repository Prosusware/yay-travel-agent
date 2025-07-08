#!/usr/bin/env python3
"""
Test script for the hotels tool.
"""
import asyncio
import os
import sys
from dotenv import load_dotenv
from serpapi import SerpApiClient as SerpApiSearch

# Add the parent directory to the path so we can import from server
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()
API_KEY = os.getenv("SERPAPI_API_KEY")

async def test_hotels_tool():
    """Test the hotels function logic directly"""
    print("🏨 Testing hotels tool functionality...")
    
    # Test parameters
    params = {
        "q": "Bali Resorts",
        "check_in_date": "2025-08-01",
        "check_out_date": "2025-08-03",
        "adults": 2,
        "currency": "USD",
        "gl": "us",
        "hl": "en"
    }
    
    print(f"📝 Test parameters: {params}")
    
    # Add API key and engine (same as in the actual function)
    params = {
        "api_key": API_KEY,
        "engine": "google_hotels",
        **params
    }
    
    try:
        # This mirrors the exact logic from the hotels function
        search = SerpApiSearch(params)
        data = search.get_dict()

        if not data:
            result = {"properties": [], "ads": [], "brands": [], "search_metadata": {}, "search_parameters": params, "error": "No response from SerpApi."}
        else:
            result = {
                "properties": data.get("properties", []),
                "ads": data.get("ads", []),
                "brands": data.get("brands", []),
                "search_metadata": data.get("search_metadata", {}),
                "search_parameters": data.get("search_parameters", params),
                "serpapi_pagination": data.get("serpapi_pagination", {})
            }
        
        print(f"✅ Function executed successfully!")
        print(f"📊 Response keys: {list(result.keys())}")
        
        if "error" in result:
            print(f"❌ Error in response: {result['error']}")
            return False
            
        properties = result.get("properties", [])
        ads = result.get("ads", [])
        brands = result.get("brands", [])
        
        print(f"🏨 Found {len(properties)} properties")
        print(f"📢 Found {len(ads)} ads")
        print(f"🏢 Found {len(brands)} brands")
        
        if properties or ads:
            print("✅ Hotels function returns property data properly!")
            
            # Show sample property info
            if properties:
                first_property = properties[0]
                print(f"🏨 Sample property: {first_property.get('name', 'N/A')}")
                if "rate_per_night" in first_property:
                    rate = first_property["rate_per_night"].get("lowest", "N/A")
                    print(f"💰 Rate per night: {rate}")
                print(f"⭐ Rating: {first_property.get('overall_rating', 'N/A')}")
            
            # Show metadata
            metadata = result.get("search_metadata", {})
            print(f"🔍 Search ID: {metadata.get('id', 'N/A')}")
            print(f"📈 Status: {metadata.get('status', 'N/A')}")
            
            return True
        else:
            print("❌ No properties or ads found in response")
            print(f"Available data keys: {list(data.keys()) if 'data' in locals() else 'No data'}")
            return False
            
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_hotels_tool())
    print(f"\n{'✅ HOTELS TEST PASSED' if success else '❌ HOTELS TEST FAILED'}")