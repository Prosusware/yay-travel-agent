from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, Field

from app.api.schemas import BookingResponse, extract_booking_result
from app.services.booking_agent import BookingAgent

router = APIRouter()


class DeliveryInfo(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    address: str
    city: str
    country: str


class FoodDeliveryRequest(BaseModel):
    # Conversation tracking
    conversation_id: str = Field(description="Unique conversation identifier")
    agent_id: str = Field(description="Agent identifier")
    agent_type: str = Field(description="Type of agent")
    
    # Booking details
    initial_url: Optional[str] = None
    cuisine: str
    dishes: Optional[List[str]] = None
    delivery_address: Optional[str] = None
    max_eta: Optional[str] = None
    budget: Optional[str] = None
    delivery_info: Optional[DeliveryInfo] = None


@router.post("/food/book", response_model=BookingResponse)
async def order_food(request: FoodDeliveryRequest):
    try:
        async with BookingAgent() as agent:
            agent_result = await agent.order_food_delivery(**request.dict())

        result = extract_booking_result(agent_result)
        return BookingResponse(result=result)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Food delivery order failed: {str(e)}"
        )
