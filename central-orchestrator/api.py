from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os
import logging
from datetime import datetime

# Import the tool calling agent
from tool_calling_agent import run_tool_calling_agent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Tool Calling Agent API",
    description="API for running the tool calling agent.",
    version="1.0.0"
)

class AgentRequest(BaseModel):
    user_id: str
    conversation_id: str
    task: str
    max_iterations: Optional[int] = 10

class AgentResponse(BaseModel):
    status: str
    message: str
    user_id: str
    conversation_id: str
    task: str
    timestamp: str

@app.post("/invoke", response_model=AgentResponse, status_code=202)
async def invoke_agent(request: AgentRequest, background_tasks: BackgroundTasks) -> AgentResponse:
    """
    Run the tool calling agent with the specified task, user_id, and conversation_id.
    This endpoint will return immediately and the agent will run in the background.
    """
    try:
        logger.info(f"🚀 Received request to start agent for user '{request.user_id}' with task: {request.task}")

        background_tasks.add_task(
            run_tool_calling_agent,
            task=request.task,
            user_id=request.user_id,
            conversation_id=request.conversation_id,
            max_iterations=10
        )

        response = AgentResponse(
            status="accepted",
            message="Agent task has been accepted and is running in the background.",
            user_id=request.user_id,
            conversation_id=request.conversation_id,
            task=request.task,
            timestamp=datetime.now().isoformat()
        )
        
        logger.info(f"✅ Agent task for user '{request.user_id}' has been successfully started in the background.")
        return response

    except Exception as e:
        error_msg = f"Failed to start agent task: {str(e)}"
        logger.error(f"❌ {error_msg}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=error_msg
        )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port) 