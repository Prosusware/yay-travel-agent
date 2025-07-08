"""
Shared API schemas and utility functions for booking operations.
"""

from pydantic import BaseModel
from typing import Optional, Any, Dict, List


class BookingResult(BaseModel):
    """Structured result from booking agent execution."""
    final_result: str
    success: bool
    steps_completed: int
    execution_time_seconds: Optional[float] = None
    error_message: Optional[str] = None
    booking_details: Optional[Dict[str, Any]] = None


class BookingResponse(BaseModel):
    result: BookingResult


class DownloadFileObject(BaseModel):
    """Downloaded file object from Skyvern task."""
    file_id: str
    file_name: str
    file_url: str
    file_size: Optional[int] = None


class WebhookRequest(BaseModel):
    """Webhook request schema from Skyvern when task completes."""
    run_id: str
    run_type: str
    status: str
    output: Optional[str] = None
    downloaded_files: Optional[List[DownloadFileObject]] = None
    recording_url: Optional[str] = None
    screenshot_urls: Optional[List[str]] = None
    failure_reason: Optional[str] = None
    app_url: Optional[str] = None
    created_at: str
    modified_at: str


class WebhookResponse(BaseModel):
    """Response schema for webhook endpoint."""
    message: str
    status: str


def extract_booking_result(agent_history: Any) -> BookingResult:
    """Extract structured information from AgentHistoryList."""
    try:
        # Extract final result
        if (hasattr(agent_history, 'final_result') and 
                agent_history.final_result):
            final_result = str(agent_history.final_result)
        elif (hasattr(agent_history, 'all_results') and 
              agent_history.all_results):
            final_result = str(agent_history.all_results[-1])
        else:
            final_result = str(agent_history)
        
        # Extract metadata
        if hasattr(agent_history, 'all_results'):
            steps_completed = len(agent_history.all_results)
        else:
            steps_completed = 0
        
        # Determine success based on final result content
        success = ("successfully" in final_result.lower() or 
                   "booked" in final_result.lower() or
                   "ordered" in final_result.lower() or
                   "delivered" in final_result.lower())
        
        # Extract any booking-specific details
        booking_details = None
        if hasattr(agent_history, 'metadata'):
            booking_details = agent_history.metadata
        
        return BookingResult(
            final_result=final_result,
            success=success,
            steps_completed=steps_completed,
            booking_details=booking_details
        )
    
    except Exception as e:
        return BookingResult(
            final_result=str(agent_history),
            success=False,
            steps_completed=0,
            error_message=f"Error extracting result: {str(e)}"
        )