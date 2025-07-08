"""
Webhook endpoints for handling external service notifications.
"""

from fastapi import APIRouter, HTTPException
from app.api.schemas import WebhookRequest, WebhookResponse
import logging
import httpx
import json

router = APIRouter()

logger = logging.getLogger(__name__)


async def _write_completion_status(conversation_id: str, agent_id: str, 
                                   agent_type: str, run_id: str, status: str, 
                                   booking_details: dict, failure_reason: str = None):
    """Write completion status to the global tools API."""
    try:
        # Prepare the status update message
        if status.lower() == 'completed':
            update_message = f"Booking completed successfully (Run ID: {run_id})"
            if booking_details:
                if booking_details.get("booking_confirmation_number"):
                    update_message += f" - Confirmation: {booking_details['booking_confirmation_number']}"
                if booking_details.get("total_price"):
                    update_message += f" - Price: {booking_details['total_price']}"
                if booking_details.get("departure_city") and booking_details.get("destination_city"):
                    update_message += f" - Route: {booking_details['departure_city']} to {booking_details['destination_city']}"
        else:
            update_message = f"Booking failed (Run ID: {run_id})"
            if failure_reason:
                update_message += f" - Reason: {failure_reason}"
        
        # Add booking details to the message
        if booking_details:
            update_message += f" - Details: {json.dumps(booking_details)}"
        
        # Prepare the payload for the status API
        payload = {
            "agent_id": agent_id,
            "agent_type": agent_type,
            "conversation_id": conversation_id,
            "update": update_message
        }
        
        # Write to the global tools API
        # Note: Using the base URL from API_INSTRUCTIONS.md
        api_url = "https://global-tools-api-534113739138.europe-west1.run.app/api/status/write"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(api_url, json=payload, timeout=30.0)
            response.raise_for_status()
            logger.info(f"Successfully wrote completion status for conversation {conversation_id}")
            
    except Exception as e:
        logger.error(f"Failed to write completion status: {str(e)}")
        # Don't raise the exception to avoid breaking the webhook processing


@router.post("/webhooks/task-complete", response_model=WebhookResponse)
async def handle_task_completion(webhook_data: WebhookRequest):
    """
    Handle Skyvern task completion webhook.
    
    This endpoint receives notifications when a Skyvern task completes,
    processes the result, and stores it in the appropriate database.
    """
    try:
        logger.info(
            f"Received webhook for task {webhook_data.run_id} "
            f"with status {webhook_data.status}"
        )
        
        # Parse the output to extract conversation tracking and booking details
        conversation_id = "unknown"
        agent_id = "unknown"
        agent_type = "unknown"
        booking_details = {}
        
        try:
            if webhook_data.output:
                # Try to parse the output as JSON to extract structured data
                if isinstance(webhook_data.output, str):
                    try:
                        output_data = json.loads(webhook_data.output)
                        conversation_id = output_data.get("conversation_id", "unknown")
                        agent_id = output_data.get("agent_id", "unknown")
                        agent_type = output_data.get("agent_type", "unknown")
                        booking_details = output_data.get("booking_details", {})
                    except json.JSONDecodeError:
                        # If not JSON, treat as plain text
                        booking_details = {"raw_output": webhook_data.output}
                else:
                    booking_details = webhook_data.output
        except Exception as e:
            logger.error(f"Error parsing webhook output: {str(e)}")
            booking_details = {"raw_output": str(webhook_data.output)}
        
        # Write completion status to the global tools API
        await _write_completion_status(
            conversation_id=conversation_id,
            agent_id=agent_id,
            agent_type=agent_type,
            run_id=webhook_data.run_id,
            status=webhook_data.status,
            booking_details=booking_details,
            failure_reason=webhook_data.failure_reason
        )
        
        # Check if task succeeded
        if webhook_data.status.lower() == 'completed':
            logger.info(f"Task {webhook_data.run_id} completed successfully")
            message = (
                f"Task {webhook_data.run_id} completed successfully "
                f"and result saved to database"
            )
            
        else:
            logger.warning(
                f"Task {webhook_data.run_id} failed with status "
                f"{webhook_data.status}: {webhook_data.failure_reason}"
            )
            message = (
                f"Task {webhook_data.run_id} failed and failure details "
                f"saved to vector database"
            )
        
        return WebhookResponse(
            message=message,
            status="processed"
        )
        
    except Exception as e:
        logger.error(f"Error processing webhook for task {webhook_data.run_id}: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to process webhook: {str(e)}"
        ) 