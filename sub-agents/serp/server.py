from fastmcp import FastMCP
from typing import Dict, Any
import os
import httpx
from dotenv import load_dotenv
from serpapi import SerpApiClient as SerpApiSearch

# Load environment variables from .env file
load_dotenv()
API_KEY = os.getenv("SERPAPI_API_KEY")

# Ensure API key is present
if not API_KEY:
    raise ValueError("SERPAPI_API_KEY not found in environment variables. Please set it in the .env file.")

# Initialize the MCP server
mcp = FastMCP("SerpApi MCP Server")

# Tool to perform searches via SerpApi
@mcp.tool()
async def search(params: Dict[str, Any] = {}) -> str:
    """Perform a search on the specified engine using SerpApi.

    Args:
        params: Dictionary of engine-specific parameters (e.g., {"q": "Coffee", "engine": "google_light", "location": "Austin, TX"}).

    Returns:
        A formatted string of search results or an error message.
    """

    params = {
        "api_key": API_KEY,
        "engine": "google_light", # Fastest engine by default
        **params  # Include any additional parameters
    }

    try:
        search = SerpApiSearch(params)
        data = search.get_dict()


        # Process organic search results if available
        if "organic_results" in data:
            formatted_results = []
            for result in data.get("organic_results", []):
                title = result.get("title", "No title")
                link = result.get("link", "No link")
                snippet = result.get("snippet", "No snippet")
                formatted_results.append(f"Title: {title}\nLink: {link}\nSnippet: {snippet}\n")
            return "\n".join(formatted_results) if formatted_results else "No organic results found"
        else:
            return "No organic results found"

    # Handle HTTP-specific errors
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 429:
            return "Error: Rate limit exceeded. Please try again later."
        elif e.response.status_code == 401:
            return "Error: Invalid API key. Please check your SERPAPI_API_KEY."
        else:
            return f"Error: {e.response.status_code} - {e.response.text}"
    # Handle other exceptions (e.g., network issues)
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool(
    annotations={
        "title": "Search Flights",
    }
)
async def flights(
    params: Dict[str, Any] = {}
) -> dict:
    """Search for flights using SerpApi's Google Flights API.

    Parameters:
        params (dict): Dictionary of flight search parameters. Example keys:
            - departure_id (str): Departure airport IATA code (e.g. 'LHR')
            - arrival_id (str): Arrival airport IATA code (e.g. 'FCO')
            - outbound_date (str): Outbound date in YYYY-MM-DD format
            - return_date (str): Return date in YYYY-MM-DD format (for round trip)
            - type (int): 1=Round trip, 2=One way, 3=Multi-city
            - adults (int): Number of adults
            - children (int): Number of children
            - travel_class (int): 1=Economy, 2=Premium economy, 3=Business, 4=First
            - currency (str): Currency code (e.g. 'USD')
            - stops (int): 0=Any, 1=Nonstop, 2=1 stop or fewer, 3=2 stops or fewer
            - sort_by (int): 1=Top, 2=Price, 3=Departure time, 4=Arrival time, 5=Duration, 6=Emissions
            - ... (see SerpApi docs for full list)

    Returns:
        dict: {"flights": [...], "search_metadata": {...}, "search_parameters": {...}}
    """
    params = {
        "api_key": API_KEY,
        "engine": "google_flights",
        **params
    }
    try:
        search = SerpApiSearch(params)
        data = search.get_dict()

        if not data:
            return {"flights": [], "search_metadata": {}, "search_parameters": params, "error": "No response from SerpApi."}

        # Return the raw best_flights and other_flights arrays as a single list
        flights = []
        if "best_flights" in data and data["best_flights"]:
            flights.extend(data["best_flights"])
        if "other_flights" in data and data["other_flights"]:
            flights.extend(data["other_flights"])

        return {
            "flights": flights,
            "search_metadata": data.get("search_metadata", {}),
            "search_parameters": data.get("search_parameters", params)
        }

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 429:
            return {"flights": [], "error": "Error: Rate limit exceeded. Please try again later."}
        elif e.response.status_code == 401:
            return {"flights": [], "error": "Error: Invalid API key. Please check your SERPAPI_API_KEY."}
        else:
            return {"flights": [], "error": f"Error: {e.response.status_code} - {e.response.text}"}
    except Exception as e:
        return {"flights": [], "error": f"Error: {str(e)}"}

@mcp.tool(
    annotations={
        "title": "Search Hotels",
    }
)
async def hotels(
    params: Dict[str, Any] = {}
) -> dict:
    """Search for hotels using SerpApi's Google Hotels API.

    Parameters:
        params (dict): Dictionary of hotel search parameters. Example keys:
            - q (str): Search query (e.g. 'hotels in Paris' or 'Hilton Tokyo')
            - check_in_date (str): Check-in date in YYYY-MM-DD format (required)
            - check_out_date (str): Check-out date in YYYY-MM-DD format (required)
            - adults (int): Number of adults (default: 2)
            - children (int): Number of children (default: 0)
            - children_ages (str): Ages of children, comma-separated (e.g. '5,8,10')
            - currency (str): Currency code (e.g. 'USD')
            - gl (str): Country code for localization (e.g. 'us')
            - hl (str): Language code (e.g. 'en')
            - sort_by (int): 3=Lowest price, 8=Highest rating, 13=Most reviewed
            - min_price (int): Minimum price per night
            - max_price (int): Maximum price per night
            - property_types (str): Property type IDs, comma-separated
            - amenities (str): Amenity IDs, comma-separated
            - rating (int): 7=3.5+, 8=4.0+, 9=4.5+
            - hotel_class (str): Hotel class, comma-separated (e.g. '2,3,4,5')
            - vacation_rentals (bool): Set to true for vacation rentals
            - ... (see SerpApi docs for full list)

    Returns:
        dict: {"properties": [...], "ads": [...], "brands": [...], "search_metadata": {...}}
    """
    params = {
        "api_key": API_KEY,
        "engine": "google_hotels",
        **params
    }
    try:
        search = SerpApiSearch(params)
        data = search.get_dict()

        if not data:
            return {"properties": [], "ads": [], "brands": [], "search_metadata": {}, "search_parameters": params, "error": "No response from SerpApi."}

        return {
            "properties": data.get("properties", []),
            "ads": data.get("ads", []),
            "brands": data.get("brands", []),
            "search_metadata": data.get("search_metadata", {}),
            "search_parameters": data.get("search_parameters", params),
            "serpapi_pagination": data.get("serpapi_pagination", {})
        }

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 429:
            return {"properties": [], "ads": [], "brands": [], "error": "Error: Rate limit exceeded. Please try again later."}
        elif e.response.status_code == 401:
            return {"properties": [], "ads": [], "brands": [], "error": "Error: Invalid API key. Please check your SERPAPI_API_KEY."}
        else:
            return {"properties": [], "ads": [], "brands": [], "error": f"Error: {e.response.status_code} - {e.response.text}"}
    except Exception as e:
        return {"properties": [], "ads": [], "brands": [], "error": f"Error: {str(e)}"}

@mcp.tool(
    annotations={
        "title": "Search Maps",
    }
)
async def maps(
    params: Dict[str, Any] = {}
) -> dict:
    """Search for local places using SerpApi's Google Maps API.

    Parameters:
        params (dict): Dictionary of maps search parameters. Example keys:
            - q (str): Search query (e.g. 'coffee shops', 'restaurants near me')
            - ll (str): Latitude and longitude coordinates (e.g. '@40.7455096,-74.0083012,14z')
            - type (str): Search type (default: 'search')
            - hl (str): Language code (e.g. 'en')
            - gl (str): Country code (e.g. 'us')
            - google_domain (str): Google domain (e.g. 'google.com')
            - ... (see SerpApi docs for full list)

    Returns:
        dict: {"local_results": [...], "search_metadata": {...}, "search_parameters": {...}}
    """
    params = {
        "api_key": API_KEY,
        "engine": "google_maps",
        **params
    }
    try:
        search = SerpApiSearch(params)
        data = search.get_dict()

        if not data:
            return {"local_results": [], "search_metadata": {}, "search_parameters": params, "error": "No response from SerpApi."}

        return {
            "local_results": data.get("local_results", []),
            "search_metadata": data.get("search_metadata", {}),
            "search_parameters": data.get("search_parameters", params),
            "search_information": data.get("search_information", {})
        }

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 429:
            return {"local_results": [], "error": "Error: Rate limit exceeded. Please try again later."}
        elif e.response.status_code == 401:
            return {"local_results": [], "error": "Error: Invalid API key. Please check your SERPAPI_API_KEY."}
        else:
            return {"local_results": [], "error": f"Error: {e.response.status_code} - {e.response.text}"}
    except Exception as e:
        return {"local_results": [], "error": f"Error: {str(e)}"}

@mcp.tool(
    annotations={
        "title": "Search Amazon",
    }
)
async def amazon(
    params: Dict[str, Any] = {}
) -> dict:
    """Search for products using SerpApi's Amazon Search API.

    Parameters:
        params (dict): Dictionary of Amazon search parameters. Example keys:
            - k (str): Search query/keywords (e.g. 'coffee', 'wireless headphones')
            - amazon_domain (str): Amazon domain (default: 'amazon.com')
            - language (str): Language code (default: 'en_US')
            - device (str): Device type (default: 'desktop')
            - page (int): Page number for pagination
            - ... (see SerpApi docs for full list)

    Returns:
        dict: {"organic_results": [...], "product_ads": {...}, "search_metadata": {...}}
    """
    params = {
        "api_key": API_KEY,
        "engine": "amazon",
        **params
    }
    try:
        search = SerpApiSearch(params)
        data = search.get_dict()

        if not data:
            return {"organic_results": [], "product_ads": {}, "search_metadata": {}, "search_parameters": params, "error": "No response from SerpApi."}

        return {
            "organic_results": data.get("organic_results", []),
            "product_ads": data.get("product_ads", {}),
            "search_metadata": data.get("search_metadata", {}),
            "search_parameters": data.get("search_parameters", params),
            "search_information": data.get("search_information", {})
        }

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 429:
            return {"organic_results": [], "product_ads": {}, "error": "Error: Rate limit exceeded. Please try again later."}
        elif e.response.status_code == 401:
            return {"organic_results": [], "product_ads": {}, "error": "Error: Invalid API key. Please check your SERPAPI_API_KEY."}
        else:
            return {"organic_results": [], "product_ads": {}, "error": f"Error: {e.response.status_code} - {e.response.text}"}
    except Exception as e:
        return {"organic_results": [], "product_ads": {}, "error": f"Error: {str(e)}"}

# Run the server
if __name__ == "__main__":
    # Note that Claude Code requires this to be run with the STDIO transport adapter (npx mcp-remote) or simply with mcp.run()
    port = int(os.environ.get("PORT", 8080))
    mcp.run(transport="http", host="0.0.0.0", port=port, path="/mcp")
