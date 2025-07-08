from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, Field

from app.api.schemas import BookingResponse, extract_booking_result
from app.services.booking_agent import BookingAgent

router = APIRouter()


class TravelerInfo(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    address: str
    city: str
    country: str
    postal_code: str


class FlightBookingRequest(BaseModel):
    # Conversation tracking
    conversation_id: str = Field(description="Unique conversation identifier")
    agent_id: str = Field(description="Agent identifier")
    agent_type: str = Field(description="Type of agent")
    
    # Booking details
    initial_url: Optional[str] = None
    direct_booking_link: Optional[str] = Field(
        default=None,
        description="Direct booking link (e.g., Ryanair flight selection URL)"
    )
    departure: str
    destination: str
    trip_type: Optional[str] = Field(
        default="Round Trip", description="'Round Trip' or 'One Way'"
    )
    departure_date: Optional[str] = None
    return_date: Optional[str] = None
    budget: Optional[str] = None
    preferred_airlines: Optional[List[str]] = None
    num_travelers: Optional[int] = 1
    traveler_info: Optional[TravelerInfo] = None


@router.post("/flights/book", response_model=BookingResponse)
async def book_flight(request: FlightBookingRequest):
    try:
        async with BookingAgent() as agent:
            agent_result = await agent.book_flight(**request.model_dump())

        result = extract_booking_result(agent_result)
        return BookingResponse(result=result)
    except Exception as e:
        error_msg = f"Flight booking failed: {str(e)}"
        raise HTTPException(status_code=500, detail=error_msg)


class DirectBookingRequest(BaseModel):
    # Conversation tracking
    conversation_id: str = Field(description="Unique conversation identifier")
    agent_id: str = Field(description="Agent identifier")
    agent_type: str = Field(description="Type of agent")
    
    # Booking details
    direct_booking_link: str = Field(
        description="Direct booking link (e.g., Booking.com, Ryanair, etc.)"
    )
    # Optional flight details (may override URL parameters)
    departure: Optional[str] = Field(
        default=None, description="Override departure city from URL"
    )
    destination: Optional[str] = Field(
        default=None, description="Override destination city from URL"
    )
    trip_type: Optional[str] = Field(
        default="Round Trip", description="'Round Trip' or 'One Way'"
    )
    departure_date: Optional[str] = Field(
        default=None, description="Override departure date from URL"
    )
    return_date: Optional[str] = Field(
        default=None, description="Override return date from URL"
    )
    budget: Optional[str] = None
    preferred_airlines: Optional[List[str]] = None
    num_travelers: Optional[int] = Field(
        default=1, description="Override number of travelers from URL"
    )
    # Required traveler information for completing the booking
    traveler_info: TravelerInfo = Field(
        description="Traveler details needed to complete the booking"
    )


@router.post("/flights/book-direct", response_model=BookingResponse)
async def book_direct_flight(request: DirectBookingRequest):
    """
    Book a flight using a direct booking link with comprehensive flight details.
    
    This endpoint accepts a direct booking link from various providers 
    and completes the booking process.
    
    The direct link may already contain flight details, but you can override
    or supplement them with additional parameters like departure/destination
    cities, dates, traveler count, etc.
    
    Required:
    - direct_booking_link: The checkout/booking URL
    - traveler_info: Complete traveler details for booking completion
    
    Optional (will override URL parameters if provided):
    - departure, destination, dates, traveler count, budget, etc.
    """
    try:
        async with BookingAgent() as agent:
            agent_result = await agent.book_direct_link(**request.model_dump())

        result = extract_booking_result(agent_result)
        return BookingResponse(result=result)
    except Exception as e:
        error_msg = f"Direct booking failed: {str(e)}"
        raise HTTPException(status_code=500, detail=error_msg)
