#!/usr/bin/env python3
"""
Test script to test the flights tool on production server.
"""

import httpx
import json
import asyncio

async def test_flights_production():
    url = "https://serp-mcp-534113739138.europe-west1.run.app/mcp/"

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream"
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        # Test 1: Initialize
        print("🧪 Testing MCP server initialization...")
        init_payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }

        response = await client.post(url, headers=headers, json=init_payload)
        print(f"Init Status: {response.status_code}")
        
        session_id = None
        if response.status_code == 200:
            # Extract session ID from Set-Cookie header if present
            set_cookie = response.headers.get('set-cookie', '')
            if 'session_id=' in set_cookie:
                session_id = set_cookie.split('session_id=')[1].split(';')[0]
                print(f"Session ID: {session_id}")
                headers['Cookie'] = f'session_id={session_id}'

            print("✅ Server initialization successful!")
            
            # Test 2: List tools
            print("\n🔧 Testing tools/list...")
            tools_payload = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list"
            }
            
            response = await client.post(url, headers=headers, json=tools_payload)
            if response.status_code == 200:
                content = response.text
                print(f"Tools available: {content[:300]}...")
            
            # Test 3: Call flights tool
            print("\n✈️  Testing flights tool...")
            flights_payload = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "flights",
                    "arguments": {
                        "params": {
                            "departure_id": "LAX",
                            "arrival_id": "JFK", 
                            "outbound_date": "2025-08-01",
                            "return_date": "2025-08-08",
                            "adults": 1,
                            "currency": "USD"
                        }
                    }
                }
            }

            response = await client.post(url, headers=headers, json=flights_payload)
            print(f"Flights Status: {response.status_code}")
            
            if response.status_code == 200:
                content = response.text
                print("✅ Flights tool called successfully!")
                
                # Parse SSE response
                if "event: message" in content:
                    lines = content.split('\n')
                    for line in lines:
                        if line.startswith('data: '):
                            try:
                                data = json.loads(line[6:])
                                result = data.get('result', {})
                                if 'content' in result:
                                    flight_data = result['content']
                                    if isinstance(flight_data, list) and len(flight_data) > 0:
                                        flight_result = flight_data[0].get('text', '')
                                        try:
                                            parsed_result = json.loads(flight_result)
                                            print(f"🛫 Response keys: {list(parsed_result.keys())}")
                                            flights = parsed_result.get('flights', [])
                                            print(f"🛫 Found {len(flights)} flights")
                                            if flights:
                                                print("✅ Flights tool returns flight data properly!")
                                                # Show first flight details
                                                first_flight = flights[0]
                                                if 'flights' in first_flight:
                                                    print(f"Sample flight: {first_flight['flights'][0]['departure_airport']['name']} -> {first_flight['flights'][0]['arrival_airport']['name']}")
                                                    print(f"Price: ${first_flight.get('price', 'N/A')}")
                                            else:
                                                print("❌ No flights in response")
                                                if 'error' in parsed_result:
                                                    print(f"Error: {parsed_result['error']}")
                                        except json.JSONDecodeError:
                                            print(f"Raw flight result: {flight_result[:500]}...")
                                    else:
                                        print(f"Unexpected result format: {result}")
                                break
                            except json.JSONDecodeError as e:
                                print(f"Failed to parse JSON: {e}")
                else:
                    print(f"Raw response: {content[:500]}...")
            else:
                print(f"❌ Flights tool failed: {response.status_code}")
                print(f"Response: {response.text}")
        else:
            print(f"❌ Server initialization failed: {response.status_code}")
            print(f"Response: {response.text}")

if __name__ == "__main__":
    asyncio.run(test_flights_production())