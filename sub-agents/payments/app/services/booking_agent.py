"""
Booking Agent Class
A class-based system for handling flight, hotel, and food delivery bookings
"""

from urllib.parse import parse_qs, urlparse
from skyvern import Skyvern
import httpx
import logging

from app.core.config import settings
from app.services.prompts import (
    FLIGHT_BOOKING_PROMPT,
    FOOD_DELIVERY_PROMPT,
    HOTEL_BOOKING_PROMPT,
    DIRECT_BOOKING_PROMPT,
)


class BookingAgent:
    """
    A class to handle different types of bookings (flights, hotels, food)
    using skyvern for browser automation.
    """

    def __init__(self):
        """Initialize the booking agent with skyvern client."""
        # Initialize skyvern client
        # Check if we have a skyvern API key, otherwise use localhost
        self.skyvern = Skyvern(api_key=settings.skyvern_api_key)
        self.logger = logging.getLogger(__name__)

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - cleanup if needed."""
        # No cleanup needed for skyvern client
        pass

    def _parse_booking_url(self, url):
        """
        Parse booking URL to extract search parameters.
        
        Args:
            url (str): Direct booking URL (e.g., Ryanair)
            
        Returns:
            dict: Parsed parameters from the URL
        """
        parsed_url = urlparse(url)
        params = parse_qs(parsed_url.query)
        
        # Extract single values from lists
        extracted_params = {}
        for key, value_list in params.items():
            if value_list:
                extracted_params[key] = value_list[0]
        
        return {
            'domain': parsed_url.netloc,
            'path': parsed_url.path,
            'params': extracted_params
        }

    async def _write_initial_status(self, conversation_id: str, agent_id: str,
                                   agent_type: str, booking_type: str,
                                   run_id: str = None):
        """Write initial status update when booking task is started."""
        try:
            # Prepare the status update message
            if run_id:
                update_message = (f"Started {booking_type} booking process "
                                f"(Run ID: {run_id})")
            else:
                update_message = f"Started {booking_type} booking process"
            
            # Prepare the payload for the status API
            payload = {
                "agent_id": agent_id,
                "agent_type": agent_type,
                "conversation_id": conversation_id,
                "update": update_message
            }
            
            # Write to the global tools API
            api_url = ("https://global-tools-api-534113739138."
                      "europe-west1.run.app/api/status/write")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(api_url, json=payload, 
                                           timeout=30.0)
                response.raise_for_status()
                self.logger.info(f"Successfully wrote initial status for "
                               f"conversation {conversation_id}")
                
        except Exception as e:
            self.logger.error(f"Failed to write initial status: {str(e)}")
            # Don't raise the exception to avoid breaking the booking process

    async def _run_agent(self, task, initial_url=None, conversation_id=None, 
                         agent_id=None, agent_type=None, booking_type=None):
        """
        Run the skyvern agent with a specific task.

        Args:
            task (str): The booking task to execute
            initial_url (str): Optional initial URL to start with
            conversation_id (str): Unique conversation identifier
            agent_id (str): Agent identifier
            agent_type (str): Type of agent
            booking_type (str): Type of booking (Flight, Hotel, Food, etc.)

        Returns:
            str: Result from the agent execution
        """
        try:
            # If initial_url is provided, include it in the task prompt
            if initial_url:
                full_task = f"Start by navigating to {initial_url}. " \
                           f"Then, {task}"
            else:
                full_task = task
            
            # Construct webhook URL
            webhook_url = (
                f"{settings.webhook_base_url}/api/v1/webhooks/task-complete"
            )
            
            # Define data extraction schema
            data_extraction_schema = {
                "conversation_id": conversation_id or "unknown",
                "agent_id": agent_id or "unknown",
                "agent_type": agent_type or "unknown",
                "booking_details": {
                    "booking_confirmation_number": "string",
                    "booking_status": "string",
                    "total_price": "string",
                    "departure_city": "string",
                    "destination_city": "string",
                    "departure_date": "string",
                    "return_date": "string",
                    "airline": "string",
                    "flight_number": "string",
                    "hotel_name": "string",
                    "check_in_date": "string",
                    "check_out_date": "string",
                    "restaurant_name": "string",
                    "cuisine_type": "string",
                    "delivery_address": "string",
                    "estimated_delivery_time": "string"
                }
            }
            
            # Run the skyvern task
            result = await self.skyvern.run_task(
                prompt=full_task,
                webhook_url=webhook_url,
                data_extraction_schema=data_extraction_schema
            )
            
            # Write initial status update after task is started
            if conversation_id and agent_id and agent_type:
                await self._write_initial_status(
                    conversation_id=conversation_id,
                    agent_id=agent_id,
                    agent_type=agent_type,
                    booking_type=booking_type or "Booking",
                    run_id=str(result) if result else None
                )
            
            return str(result)
        except Exception as e:
            return f"Error running skyvern task: {str(e)}"

    def _create_flight_task_prompt(self, **kwargs):
        """
        Create a flight booking task prompt.

        Args:
            **kwargs: Flight booking parameters

        Returns:
            str: Formatted task prompt
        """
        booking_details = f"""
        - Departure: {kwargs.get('departure')}
        - Destination: {kwargs.get('destination')}
        - Trip Type: {kwargs.get('trip_type', 'Round Trip')}
        """

        if kwargs.get("departure_date"):
            booking_details += f"- Departure Date: {kwargs['departure_date']}\n"
        if (kwargs.get("return_date") and
                kwargs.get("trip_type") == "Round Trip"):
            booking_details += f"- Return Date: {kwargs['return_date']}\n"
        if kwargs.get("budget"):
            booking_details += f"- Budget: {kwargs['budget']}\n"
        if kwargs.get("preferred_airlines"):
            airlines_str = (
                ", ".join(kwargs["preferred_airlines"])
                if isinstance(kwargs["preferred_airlines"], list)
                else kwargs["preferred_airlines"]
            )
            booking_details += f"- Preferred Airlines: {airlines_str}\n"

        booking_details += (
            f"- Number of Travelers: {kwargs.get('num_travelers', 1)}"
        )

        traveler_info = kwargs.get(
            "traveler_info",
            {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com",
                "phone": "+1234567890",
                "address": "123 Main St",
                "city": "Anytown",
                "country": "USA",
            },
        )

        return self._TASK_TEMPLATE.format(
            booking_type="Flight",
            booking_details=booking_details,
            **traveler_info,
        )

    def _create_hotel_task_prompt(self, **kwargs):
        """
        Create a hotel booking task prompt.

        Args:
            **kwargs: Hotel booking parameters

        Returns:
            str: Formatted task prompt
        """
        booking_details = f"""
        - City: {kwargs.get('city')}
        """

        if kwargs.get("location_preference"):
            booking_details += (
                f"- Preferred Location: {kwargs['location_preference']}\n"
            )
        if kwargs.get("check_in_date"):
            booking_details += f"- Check-in Date: {kwargs['check_in_date']}\n"
        if kwargs.get("check_out_date"):
            booking_details += f"- Check-out Date: {kwargs['check_out_date']}\n"
        if kwargs.get("budget"):
            booking_details += f"- Budget per Night: {kwargs['budget']}\n"
        if kwargs.get("num_guests"):
            booking_details += f"- Number of Guests: {kwargs['num_guests']}\n"
        if kwargs.get("room_type"):
            booking_details += f"- Room Type: {kwargs['room_type']}"

        traveler_info = kwargs.get(
            "traveler_info",
            {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com",
                "phone": "+1234567890",
                "address": "123 Main St",
                "city": "Anytown",
                "country": "USA",
            },
        )

        return self._TASK_TEMPLATE.format(
            booking_type="Hotel",
            booking_details=booking_details,
            **traveler_info,
        )

    def _create_food_delivery_task_prompt(self, **kwargs):
        """
        Create a food delivery task prompt.

        Args:
            **kwargs: Food delivery parameters

        Returns:
            str: Formatted task prompt
        """
        booking_details = f"""
        - Cuisine: {kwargs.get('cuisine')}
        """

        if kwargs.get("dishes"):
            dishes_str = (
                ", ".join(kwargs["dishes"])
                if isinstance(kwargs["dishes"], list)
                else kwargs["dishes"]
            )
            booking_details += f"- Dishes: {dishes_str}\n"
        if kwargs.get("delivery_address"):
            booking_details += (
                f"- Delivery Address: {kwargs['delivery_address']}\n"
            )
        if kwargs.get("max_eta"):
            booking_details += (
                f"- Maximum Delivery Time: {kwargs['max_eta']}\n"
            )
        if kwargs.get("budget"):
            booking_details += f"- Budget: {kwargs['budget']}"

        delivery_info = kwargs.get(
            "delivery_info",
            {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com",
                "phone": "+1234567890",
                "address": "123 Main St",
                "city": "Anytown",
                "country": "USA",
            },
        )

        return self._TASK_TEMPLATE.format(
            booking_type="Food Delivery",
            booking_details=booking_details,
            **delivery_info,
        )

    async def book_flight(self, **kwargs):
        """
        Book a flight using the specialized flight booking prompt.

        Args:
            **kwargs: Flight booking parameters including:
                - initial_url: Starting URL
                - direct_booking_link: Direct booking URL (optional)
                - departure: Departure city/airport
                - destination: Destination city/airport
                - trip_type: "Round Trip" or "One Way"
                - departure_date: Departure date
                - return_date: Return date (for round trips)
                - budget: Budget constraint
                - preferred_airlines: List of preferred airlines
                - num_travelers: Number of travelers
                - traveler_info: Dictionary with traveler details

        Returns:
            str: Result from the flight booking process
        """
        # Check if direct booking link is provided
        if kwargs.get("direct_booking_link"):
            return await self.book_direct_link(**kwargs)
        
        # Use standard flight booking process
        task_prompt = self._create_flight_task_prompt(**kwargs)
        full_prompt = f"{FLIGHT_BOOKING_PROMPT}\n\n{task_prompt}"

        return await self._run_agent(
            full_prompt, 
            kwargs.get("initial_url"),
            kwargs.get("conversation_id"),
            kwargs.get("agent_id"),
            kwargs.get("agent_type"),
            "Flight"
        )

    async def book_hotel(self, **kwargs):
        """
        Book a hotel using the specialized hotel booking prompt.

        Args:
            **kwargs: Hotel booking parameters including:
                - initial_url: Starting URL
                - city: Destination city
                - location_preference: Preferred area/neighborhood
                - check_in_date: Check-in date
                - check_out_date: Check-out date
                - budget: Budget per night
                - num_guests: Number of guests
                - room_type: Preferred room type
                - traveler_info: Dictionary with traveler details

        Returns:
            str: Result from the hotel booking process
        """
        task_prompt = self._create_hotel_task_prompt(**kwargs)
        full_prompt = f"{HOTEL_BOOKING_PROMPT}\n\n{task_prompt}"

        return await self._run_agent(
            full_prompt, 
            kwargs.get("initial_url"),
            kwargs.get("conversation_id"),
            kwargs.get("agent_id"),
            kwargs.get("agent_type"),
            "Hotel"
        )

    async def order_food_delivery(self, **kwargs):
        """
        Order food delivery using the specialized food delivery prompt.

        Args:
            **kwargs: Food delivery parameters including:
                - initial_url: Starting URL
                - cuisine: Type of cuisine to order
                - dishes: Specific dishes to order
                - delivery_address: Delivery address
                - max_eta: Maximum delivery time
                - budget: Budget constraint
                - delivery_info: Dictionary with delivery details

        Returns:
            str: Result from the food delivery ordering process
        """
        task_prompt = self._create_food_delivery_task_prompt(**kwargs)
        full_prompt = f"{FOOD_DELIVERY_PROMPT}\n\n{task_prompt}"

        return await self._run_agent(
            full_prompt, 
            kwargs.get("initial_url"),
            kwargs.get("conversation_id"),
            kwargs.get("agent_id"),
            kwargs.get("agent_type"),
            "Food Delivery"
        )

    def _create_direct_booking_task_prompt(self, **kwargs):
        """
        Create a direct booking task prompt.

        Args:
            **kwargs: Direct booking parameters including url_info

        Returns:
            str: Formatted task prompt
        """
        url_info = kwargs.get("url_info", {})
        
        booking_details = f"""
        - Direct Booking Link: {kwargs.get('direct_booking_link')}
        - Booking Platform: {url_info.get('domain', 'Unknown')}
        """

        traveler_info = kwargs.get(
            "traveler_info",
            {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com",
                "phone": "+1234567890",
                "address": "123 Main St",
                "city": "Anytown",
                "country": "USA",
                "postal_code": "12345"
            },
        )

        return self._TASK_TEMPLATE.format(
            booking_type="Direct Booking",
            booking_details=booking_details,
            **traveler_info,
        )

    async def book_direct_link(self, **kwargs):
        """
        Book using a direct booking link.
        
        Args:
            **kwargs: Booking parameters including:
                - direct_booking_link: Direct URL to the booking page
                - traveler_info: Dictionary with traveler details
                
        Returns:
            str: Result from the direct booking process
        """
        direct_link = kwargs.get("direct_booking_link")
        if not direct_link:
            raise ValueError("Direct booking link is required")
        
        # Parse the URL to extract relevant information
        url_info = self._parse_booking_url(direct_link)
        
        # Create task prompt for direct booking
        task_prompt = self._create_direct_booking_task_prompt(
            url_info=url_info, **kwargs
        )
        full_prompt = f"{DIRECT_BOOKING_PROMPT}\n\n{task_prompt}"
        
        return await self._run_agent(
            full_prompt, 
            direct_link,
            kwargs.get("conversation_id"),
            kwargs.get("agent_id"),
            kwargs.get("agent_type"),
            "Direct Booking"
        )

    # Task template for formatting booking requests
    _TASK_TEMPLATE = """
{booking_type} Booking Request:

{booking_details}

Please navigate to appropriate booking sites, find the best option within the specified constraints, and complete the booking with the provided traveler information.

Traveler Information:
- First Name: {first_name}
- Last Name: {last_name}
- Email: {email}
- Phone: {phone}
- Address: {address}
- City: {city}
- Country: {country}
- Postal Code: {postal_code}
"""
