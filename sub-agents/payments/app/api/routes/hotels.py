from typing import Optional

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


class HotelBookingRequest(BaseModel):
    # Conversation tracking
    conversation_id: str = Field(description="Unique conversation identifier")
    agent_id: str = Field(description="Agent identifier")
    agent_type: str = Field(description="Type of agent")
    
    # Booking details
    initial_url: Optional[str] = None
    city: str
    location_preference: Optional[str] = None
    check_in_date: Optional[str] = None
    check_out_date: Optional[str] = None
    budget: Optional[str] = None
    num_guests: Optional[int] = None
    room_type: Optional[str] = None
    traveler_info: Optional[TravelerInfo] = None


@router.post("/hotels/book", response_model=BookingResponse)
async def book_hotel(request: HotelBookingRequest):
    try:
        async with BookingAgent() as agent:
            agent_result = await agent.book_hotel(**request.dict())

        result = extract_booking_result(agent_result)
        return BookingResponse(result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hotel booking failed: {str(e)}")
