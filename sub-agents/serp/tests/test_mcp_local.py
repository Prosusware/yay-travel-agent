#!/usr/bin/env python3
"""
Test MCP server locally using proper MCP protocol.
"""
import subprocess
import json
import asyncio
import time

async def test_mcp_local():
    print("🧪 Testing local MCP server using mcp-remote...")
    
    # Start mcp-remote as a subprocess
    process = subprocess.Popen(
        ["npx", "mcp-remote", "http://localhost:8080/mcp/"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    try:
        # Wait a moment for connection
        await asyncio.sleep(2)
        
        print("📡 Connected via mcp-remote transport")
        
        # Send initialize message
        init_message = {
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
        
        print("🔧 Sending initialize message...")
        process.stdin.write(json.dumps(init_message) + "\n")
        process.stdin.flush()
        
        # Read response
        await asyncio.sleep(1)
        
        # Send tools/list request
        tools_message = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        
        print("📋 Requesting tools list...")
        process.stdin.write(json.dumps(tools_message) + "\n")
        process.stdin.flush()
        
        await asyncio.sleep(1)
        
        # Send flights tool call
        flights_message = {
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
        
        print("✈️  Calling flights tool...")
        process.stdin.write(json.dumps(flights_message) + "\n")
        process.stdin.flush()
        
        # Wait for processing
        await asyncio.sleep(5)
        
        # Read all available output
        print("📖 Reading responses...")
        output_lines = []
        while True:
            try:
                line = process.stdout.readline()
                if not line:
                    break
                output_lines.append(line.strip())
                if len(output_lines) > 10:  # Limit output
                    break
            except:
                break
        
        print(f"📊 Received {len(output_lines)} response lines")
        
        # Look for flight results
        flight_found = False
        for line in output_lines:
            if line and line != "":
                try:
                    data = json.loads(line)
                    if "result" in data and "content" in data["result"]:
                        content = data["result"]["content"]
                        if isinstance(content, list) and len(content) > 0:
                            text_content = content[0].get("text", "")
                            if "flights" in text_content:
                                print("✅ Found flights in response!")
                                try:
                                    flight_data = json.loads(text_content)
                                    flights = flight_data.get("flights", [])
                                    print(f"🛫 Found {len(flights)} flights")
                                    flight_found = True
                                except:
                                    print("🔍 Flight data found but couldn't parse JSON")
                                    print(f"Raw content: {text_content[:200]}...")
                                    flight_found = True
                                break
                except json.JSONDecodeError:
                    continue
        
        if not flight_found:
            print("❌ No flight data found in responses")
            print("Raw output lines:")
            for i, line in enumerate(output_lines[:5]):
                print(f"  {i+1}: {line}")
        
        return flight_found
        
    except Exception as e:
        print(f"❌ Error during MCP test: {e}")
        return False
    
    finally:
        # Clean up
        try:
            process.terminate()
            process.wait(timeout=3)
        except:
            process.kill()

if __name__ == "__main__":
    success = asyncio.run(test_mcp_local())
    print(f"\n{'✅ MCP TEST PASSED' if success else '❌ MCP TEST FAILED'}")