#!/usr/bin/env python3
"""
Test script for the maps tool.
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

async def test_maps_tool():
    """Test the maps function logic directly"""
    print("🗺️  Testing maps tool functionality...")
    
    # Test parameters
    params = {
        "q": "Coffee",
        "ll": "@40.7455096,-74.0083012,14z",  # NYC coordinates
        "type": "search",
        "hl": "en",
        "gl": "us",
        "google_domain": "google.com"
    }
    
    print(f"📝 Test parameters: {params}")
    
    # Add API key and engine (same as in the actual function)
    params = {
        "api_key": API_KEY,
        "engine": "google_maps",
        **params
    }
    
    try:
        # This mirrors the exact logic from the maps function
        search = SerpApiSearch(params)
        data = search.get_dict()

        if not data:
            result = {"local_results": [], "search_metadata": {}, "search_parameters": params, "error": "No response from SerpApi."}
        else:
            result = {
                "local_results": data.get("local_results", []),
                "search_metadata": data.get("search_metadata", {}),
                "search_parameters": data.get("search_parameters", params),
                "search_information": data.get("search_information", {})
            }
        
        print(f"✅ Function executed successfully!")
        print(f"📊 Response keys: {list(result.keys())}")
        
        if "error" in result:
            print(f"❌ Error in response: {result['error']}")
            return False
            
        local_results = result.get("local_results", [])
        print(f"📍 Found {len(local_results)} local results")
        
        if local_results:
            print("✅ Maps function returns local data properly!")
            
            # Show sample location info
            first_result = local_results[0]
            print(f"☕ Sample place: {first_result.get('title', 'N/A')}")
            print(f"📍 Address: {first_result.get('address', 'N/A')}")
            print(f"⭐ Rating: {first_result.get('rating', 'N/A')}")
            print(f"📝 Reviews: {first_result.get('reviews', 'N/A')}")
            print(f"🏷️  Type: {first_result.get('type', 'N/A')}")
            
            # Show coordinates if available
            gps = first_result.get("gps_coordinates", {})
            if gps:
                print(f"🌍 Coordinates: {gps.get('latitude', 'N/A')}, {gps.get('longitude', 'N/A')}")
            
            # Show metadata
            metadata = result.get("search_metadata", {})
            print(f"🔍 Search ID: {metadata.get('id', 'N/A')}")
            print(f"📈 Status: {metadata.get('status', 'N/A')}")
            
            return True
        else:
            print("❌ No local results found in response")
            print(f"Available data keys: {list(data.keys()) if 'data' in locals() else 'No data'}")
            return False
            
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_maps_tool())
    print(f"\n{'✅ MAPS TEST PASSED' if success else '❌ MAPS TEST FAILED'}")