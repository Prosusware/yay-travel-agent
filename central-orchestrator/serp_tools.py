from typing import Dict, Any
import asyncio
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from utils import tool_wrapper


@tool_wrapper
async def serp_search(params: dict) -> Dict[str, Any]:
    """
    Perform a search on the specified engine using SerpApi via MCP.

    Args:
        params: Dictionary of engine-specific parameters (e.g., {"q": "Coffee", "engine": "google_light", "location": "Austin, TX"}).

    Returns:
        A dictionary containing the search results or an error message.
    """
    server_url = "https://serp-mcp-534113739138.europe-west1.run.app/mcp/"
    
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "mcp-remote", server_url],
        env=None
    )

    async with AsyncExitStack() as exit_stack:
        try:
            print("Connecting to MCP server for search...")
            stdio_transport = await exit_stack.enter_async_context(stdio_client(server_params))
            stdio, write = stdio_transport
            
            session = await exit_stack.enter_async_context(ClientSession(stdio, write))

            await session.initialize()

            print(f"Calling 'search' tool with params: {params}")
            result = await session.call_tool("search", params)
            
            print("Search successful.")
            return {"success": True, "result": result.content}

        except Exception as e:
            print(f"❌ An error occurred during serp_search: {e}")
            return {"success": False, "error": str(e)}

@tool_wrapper
async def flights(params: dict) -> Dict[str, Any]:
    """
    Search for flights using SerpApi's Google Flights API.

    Parameters:
        params (dict): Dictionary of flight search parameters. Example keys:
            - departure_id (str): Departure airport IATA code (e.g. 'LHR')
            - arrival_id (str): Arrival airport IATA code (e.g. 'FCO')
            - outbound_date (str): Outbound date in YYYY-MM-DD format
            - return_date (str): Return date in YYYY-MM-DD format (for round trip)
            - type (int): 1=Round trip, 2=One way, 3=Multi-city
    """
    server_url = "https://serp-mcp-534113739138.europe-west1.run.app/mcp/"
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "mcp-remote", server_url],
        env=None
    )
    async with AsyncExitStack() as exit_stack:
        try:
            stdio_transport = await exit_stack.enter_async_context(stdio_client(server_params))
            stdio, write = stdio_transport
            session = await exit_stack.enter_async_context(ClientSession(stdio, write))
            await session.initialize()
            result = await session.call_tool("flights", params)
            return {"success": True, "result": result.content}
        except Exception as e:
            return {"success": False, "error": str(e)}

@tool_wrapper
async def hotels(params: dict) -> Dict[str, Any]:
    """
    Search for hotels using SerpApi's Google Hotels API.

    Parameters:
        params (dict): Dictionary of hotel search parameters. Example keys:
            - q (str): Search query (e.g. 'hotels in Paris' or 'Hilton Tokyo')
            - check_in_date (str): Check-in date in YYYY-MM-DD format (required)
            - check_out_date (str): Check-out date in YYYY-MM-DD format (required)
            - adults (int): Number of adults (default: 2)
    """
    server_url = "https://serp-mcp-534113739138.europe-west1.run.app/mcp/"
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "mcp-remote", server_url],
        env=None
    )
    async with AsyncExitStack() as exit_stack:
        try:
            stdio_transport = await exit_stack.enter_async_context(stdio_client(server_params))
            stdio, write = stdio_transport
            session = await exit_stack.enter_async_context(ClientSession(stdio, write))
            await session.initialize()
            result = await session.call_tool("hotels", params)
            return {"success": True, "result": result.content}
        except Exception as e:
            return {"success": False, "error": str(e)}

@tool_wrapper
async def maps(params: dict) -> Dict[str, Any]:
    """
    Search for local places using SerpApi's Google Maps API.

    Parameters:
        params (dict): Dictionary of maps search parameters. Example keys:
            - q (str): Search query (e.g. 'coffee shops', 'restaurants near me')
            - ll (str): Latitude and longitude coordinates (e.g. '@40.7455096,-74.0083012,14z')
            - type (str): Search type (default: 'search')
    """
    server_url = "https://serp-mcp-534113739138.europe-west1.run.app/mcp/"
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "mcp-remote", server_url],
        env=None
    )
    async with AsyncExitStack() as exit_stack:
        try:
            stdio_transport = await exit_stack.enter_async_context(stdio_client(server_params))
            stdio, write = stdio_transport
            session = await exit_stack.enter_async_context(ClientSession(stdio, write))
            await session.initialize()
            result = await session.call_tool("maps", params)
            return {"success": True, "result": result.content}
        except Exception as e:
            return {"success": False, "error": str(e)}

@tool_wrapper
async def amazon(params: dict) -> Dict[str, Any]:
    """
    Search for products using SerpApi's Amazon Search API.

    Parameters:
        params (dict): Dictionary of Amazon search parameters. Example keys:
            - k (str): Search query/keywords (e.g. 'coffee', 'wireless headphones')
            - amazon_domain (str): Amazon domain (default: 'amazon.com')
    """
    server_url = "https://serp-mcp-534113739138.europe-west1.run.app/mcp/"
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "mcp-remote", server_url],
        env=None
    )
    async with AsyncExitStack() as exit_stack:
        try:
            stdio_transport = await exit_stack.enter_async_context(stdio_client(server_params))
            stdio, write = stdio_transport
            session = await exit_stack.enter_async_context(ClientSession(stdio, write))
            await session.initialize()
            result = await session.call_tool("amazon", params)
            return {"success": True, "result": result.content}
        except Exception as e:
            return {"success": False, "error": str(e)} 