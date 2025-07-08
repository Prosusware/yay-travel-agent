#!/usr/bin/env python3
"""
Simple test script to verify the MCP server is working.
"""

import httpx
import json
import asyncio

async def test_mcp_server():
    url = "https://serp-mcp-534113739138.europe-west1.run.app/mcp/"

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream"
    }

    async with httpx.AsyncClient() as client:
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
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            print("✅ Server responded successfully!")

            # Parse SSE response
            content = response.text
            if "event: message" in content:
                # Extract JSON from SSE format
                lines = content.split('\n')
                for line in lines:
                    if line.startswith('data: '):
                        data = json.loads(line[6:])  # Remove 'data: ' prefix
                        print(f"📋 Server Info: {data.get('result', {}).get('serverInfo', {})}")
                        print(f"🔧 Capabilities: {data.get('result', {}).get('capabilities', {})}")
                        break
        else:
            print(f"❌ Server returned error: {response.status_code}")
            print(f"Response: {response.text}")

if __name__ == "__main__":
    asyncio.run(test_mcp_server())
