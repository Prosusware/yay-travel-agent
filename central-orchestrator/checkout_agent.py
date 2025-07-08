import os
import requests
import json
from typing import Dict, Any, Optional

from utils import tool_wrapper

# Base URL for the Checkout Agent API
CHECKOUT_API_URL = os.getenv("CHECKOUT_API_URL", "https://checkout-agent-534113739138.europe-west1.run.app/api/v1")


def _make_checkout_request(endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Helper function to make requests to the Checkout Agent API.

    Args:
        endpoint: The API endpoint to call (e.g., "/flights/book").
        payload: The request payload.

    Returns:
        The JSON response from the API.
    """
    url = f"{CHECKOUT_API_URL}{endpoint}"
    headers = {
        "Content-Type": "application/json"
    }

    try:
        print(f"🚀 Calling Checkout Agent API: {url}")
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=60)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        error_message = f"HTTP error occurred: {http_err}"
        if response.text:
            error_message += f" - {response.text}"
        print(f"❌ {error_message}")
        return {"success": False, "error": error_message}
    except Exception as e:
        error_message = f"An unexpected error occurred: {e}"
        print(f"❌ {error_message}")
        return {"success": False, "error": error_message}


@tool_wrapper
def book_flight(
    traveler_info: Dict[str, str],
    conversation_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Books a specific, pre-defined flight using a hardcoded direct booking link.

    This tool is for a very specific flight booking and only requires traveler information.
    The conversation_id is injected automatically by the agent.

    Args:
        traveler_info: A dictionary with traveler details (first_name, last_name, email, phone, address, city, country, postal_code).
        conversation_id: The conversation ID for tracking. This is injected automatically.

    Returns:
        A dictionary with the booking initiation status.
    """
    if not conversation_id or not isinstance(conversation_id, str):
        raise ValueError("conversation_id must be a non-empty string and is injected by the agent")

    endpoint = "/flights/book-direct"
    direct_booking_link = "https://flights.booking.com/flights/LON.CITY-LYS.CITY?type=ONEWAY&adults=1&cabinClass=ECONOMY&children=&from=LON.CITY&to=LYS.CITY&fromCountry=GB&toCountry=FR&fromLocationName=London&toLocationName=Lyon&depart=2025-10-28&sort=BEST&travelPurpose=leisure&ca_source=flights_index_sb&aid=304142&label=gen173nr-1FCAEoggI46AdIM1gEaE2IAQGYATG4AQfIAQzYAQHoAQH4AQKIAgGoAgO4AvPLs8MGwAIB0gIkN2Y2ZTM0YmUtZWQxYS00ZDRhLTk3NDQtOTY3YWNjZmEyODhj2AIF4AIB&adplat=www-index-web_shell_header-flight-missing_creative-3SZuCfvUKIzEcXTTUh3OPb"
    
    payload = {
        "direct_booking_link": direct_booking_link,
        "traveler_info": traveler_info,
        "conversation_id": conversation_id
    }

    return _make_checkout_request(endpoint, payload) 