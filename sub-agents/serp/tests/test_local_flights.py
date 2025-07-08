#!/usr/bin/env python3
"""
Test script to test the flights tool on local server by directly importing the function.
"""
import asyncio
import sys
import os

# Add the current directory to the path so we can import server
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from server import flights

async def test_local_flights():
    print("🧪 Testing local flights tool directly...")
    
    # Test parameters
    test_params = {
        "departure_id": "LAX",
        "arrival_id": "JFK",
        "outbound_date": "2025-08-01", 
        "return_date": "2025-08-08",
        "adults": 1,
        "currency": "USD"
    }
    
    print(f"📝 Test parameters: {test_params}")
    
    try:
        # Call the flights function directly
        result = await flights(test_params)
        
        print(f"✅ Flights function executed successfully!")
        print(f"📊 Response keys: {list(result.keys())}")
        
        if "error" in result:
            print(f"❌ Error in response: {result['error']}")
            return False
            
        flights_data = result.get("flights", [])
        print(f"🛫 Found {len(flights_data)} flights")
        
        if flights_data:
            print("✅ Flights tool returns flight data properly!")
            
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
            print(f"Full result: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Error calling flights function: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_local_flights())
    print(f"\n{'✅ TEST PASSED' if success else '❌ TEST FAILED'}")