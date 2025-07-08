import os
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage
from langgraph.graph import StateGraph, END, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition

from whatsapp_tools import get_whatsapp_tools
from global_tools import get_global_tools
import mongo

# Load environment variables
load_dotenv()

# Initialize FastAPI
app = FastAPI(title="WhatsApp Agent API", version="1.0.0")

# Global variables for monitoring
processed_message_ids = set()  # Track processed messages to avoid duplicates
monitoring_logs = []  # Store monitoring activity logs
auto_fetch_task = None  # Task for auto-fetching recent messages

# Request/Response models
class TaskRequest(BaseModel):
    task: str
    user_id: Optional[str] = None
    conversation_id: Optional[str] = None
    model: Optional[str] = "llama-3.3-70b-versatile"
    max_iterations: Optional[int] = 10
    sleep_duration: Optional[int] = 30  # Default sleep duration in seconds

class TaskResponse(BaseModel):
    status: str  # "ok" or "failed"
    message: str
    execution_log: List[Dict[str, Any]]
    task_id: Optional[str] = None
    user_id: Optional[str] = None
    conversation_id: Optional[str] = None

# Agent State - extends MessagesState
class AgentState(MessagesState):
    task: str
    user_id: Optional[str]
    conversation_id: Optional[str]
    iterations: int
    max_iterations: int
    execution_log: List[Dict[str, Any]]
    task_completed: bool
    error: Optional[str]
    sleep_duration: int
    should_sleep: bool
    last_sent_message_time: Optional[str]  # Track when we last sent a message
    waiting_for_response: bool  # Flag to indicate if we're waiting for a response
    sleep_count: int  # Track how many times we've slept waiting for response

class WhatsAppAgent:
    def __init__(self, model_name: str = "llama-3.3-70b-versatile"):
        # Combine WhatsApp tools with global tools
        self.whatsapp_tools = get_whatsapp_tools()
        self.global_tools = get_global_tools()
        self.tools = self.whatsapp_tools + self.global_tools
        self.tool_node = ToolNode(self.tools)
        
        # Initialize the Groq LLM
        self.llm = ChatGroq(
            model=model_name,
            temperature=0,
            groq_api_key=os.environ.get("GROQ_API_KEY")
        )
        
        self.llm = self.llm.bind_tools(self.tools)
        
        # Create the graph
        self.graph = self._create_graph()
    
    def _create_graph(self) -> StateGraph:
        """Create the LangGraph workflow"""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("agent", self._agent_node)
        workflow.add_node("tools", self.tool_node)
        workflow.add_node("sleep", self._sleep_node)
        
        # Set entry point
        workflow.set_entry_point("agent")
        
        # Add conditional edges with custom routing logic
        workflow.add_conditional_edges(
            "agent",
            self._route_after_agent,
            {"tools": "tools", "sleep": "sleep", END: END}
        )
        workflow.add_edge("tools", "agent")
        workflow.add_edge("sleep", "agent")
        
        return workflow.compile()
    
    def _route_after_agent(self, state: AgentState) -> str:
        """Custom routing logic after agent node"""
        # Check if task is completed or failed
        if state.get("task_completed", False):
            return END
        
        # Check if agent wants to sleep
        if state.get("should_sleep", False):
            return "sleep"
        
        # Check if agent has tool calls to make
        last_message = state["messages"][-1] if state["messages"] else None
        if last_message and hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return "tools"
        
        # Default to ending if no action needed
        return END
    
    def _sleep_node(self, state: AgentState) -> AgentState:
        """Sleep node that waits for a specified duration"""
        sleep_duration = state.get("sleep_duration", 30)
        execution_log = state["execution_log"]
        waiting_for_response = state.get("waiting_for_response", False)
        sleep_count = state.get("sleep_count", 0)
        last_sent_message_time = state.get("last_sent_message_time")
        
        # Determine sleep reason for better logging
        sleep_reason = "general wait"
        if waiting_for_response:
            sleep_reason = f"waiting for response (attempt {sleep_count})"
        
        # Log the sleep action with context
        execution_log.append({
            "timestamp": datetime.now().isoformat(),
            "type": "sleep",
            "message": f"Agent entering sleep state for {sleep_duration} seconds - {sleep_reason}",
            "sleep_duration": sleep_duration,
            "sleep_count": sleep_count,
            "waiting_for_response": waiting_for_response,
            "last_sent_message_time": last_sent_message_time,
            "iteration": state["iterations"]
        })
        
        # Sleep for the specified duration
        import time
        time.sleep(sleep_duration)
        
        # Log wake up with guidance for next steps
        wake_up_message = "Agent waking up from sleep"
        if waiting_for_response:
            wake_up_message += " - will check for new responses"
        
        execution_log.append({
            "timestamp": datetime.now().isoformat(),
            "type": "wake_up",
            "message": wake_up_message,
            "iteration": state["iterations"]
        })
        
        # Reset sleep flag but maintain waiting state
        return {
            **state,
            "should_sleep": False,
            "execution_log": execution_log
        }

    def _agent_node(self, state: AgentState) -> AgentState:
        """Agent reasoning node"""
        messages = state["messages"]
        task = state["task"]
        user_id = state.get("user_id")
        conversation_id = state.get("conversation_id")
        iterations = state["iterations"]
        max_iterations = state["max_iterations"]
        execution_log = state["execution_log"]
        
        # Check if we've exceeded max iterations
        if iterations >= max_iterations:
            execution_log.append({
                "timestamp": datetime.now().isoformat(),
                "type": "error",
                "message": f"Maximum iterations ({max_iterations}) reached without completing task"
            })
            return {
                **state,
                "task_completed": True,
                "error": "Maximum iterations reached",
                "execution_log": execution_log
            }
        
        # Create the system message with context about user and conversation if available
        context_info = ""
        if user_id:
            context_info += f"\nUser ID: {user_id}"
        if conversation_id:
            context_info += f"\nConversation ID: {conversation_id}"
        
        system_message = f"""You are a Prosusware WhatsApp agent that helps people book travel trips and order food. Your task is: {task}{context_info}

You have access to these WhatsApp tools:
- list_messages: Get messages with filters and context
- list_chats: List available chats
- get_chat: Get chat information by JID
- get_direct_chat_by_contact: Find direct chat with a contact
- get_contact_chats: List all chats involving a contact
- get_last_interaction: Get most recent message with a contact
- get_message_context: Get context around a specific message (use this to understand conversation history)
- send_message: Send a message to a contact or group - 
- send_file: Send a file (image, video, document)
- send_audio_message: Send an audio message
- download_media: Download media from a message

You also have access to these Global Tools:
- web_search: Use for real-time information about travel destinations, restaurants, flight details, or current events. Particularly useful when you need up-to-date information not in your training data.
- Contact Management:
  - add_contact_tool: Create a new contact when a user mentions someone new they want to interact with. Only email is required, but collect as much information as available.
  - update_contact_tool: Update contact details when users provide new information about themselves or others.
  - get_contacts_tool: Check if a contact already exists before creating a new one, or to get a comprehensive view of a user's network. If this tool does not work then should use the list chats whatsapp tool instead.
- Memory Management:
  - add_memory_tool: IMPORTANT - Store any significant user preferences, requirements, or personal details shared during conversations. Examples: food allergies, travel preferences, important dates, family information, previous orders, etc.
  - search_memory_tool: ALWAYS search memories before making recommendations or when starting a new conversation with a returning user. This provides personalized context for better service.
- Status Tracking:
  - write_status_tool: Record important milestones in conversations (e.g., "User confirmed booking", "Waiting for payment details") to maintain state across sessions.
  - read_status_tool: Check previous conversation status before continuing a task that might have been interrupted.
- Document Management:
  - store_documents_tool: Save important structured information like menus, travel itineraries, booking confirmations, or receipts for later reference.
  - search_documents_tool: Retrieve previously stored documents when needed for reference or to continue an interrupted task.

IMPORTANT RULES:
1. Use phone numbers with country code but no + symbol (e.g., 447865463524)
2. For groups, use the whatsappJID format (e.g., <number>@g.us)
3. Be thorough in your approach - gather information before acting
4. When responding to messages, always use get_message_context to understand the conversation history
5. Consider previous conversation context when generating responses
6. CRITICAL: For GROUP chats, ALWAYS send responses to the GROUP chat using the chat JID as recipient
7. For DIRECT chats, send responses directly to the sender
8. If you need to wait or don't have anything to do right now, respond with "SLEEP" to enter sleep mode
9. Only EVER send one message per person.
10. NEVER send an identical message to the person you just sent a message to.

WHEN TO USE MEMORY TOOLS:
- ALWAYS add memories when users share:
  - Personal preferences (favorite foods, travel destinations, etc.)
  - Requirements or restrictions (dietary needs, accessibility requirements)
  - Important dates (birthdays, anniversaries, travel dates)
  - Contact details (phone numbers, addresses)
  - Feedback about previous experiences
- ALWAYS search memories:
  - At the beginning of conversations with returning users
  - Before making recommendations
  - When users reference previous interactions
  - When planning complex tasks like travel itineraries

GLOBAL TOOLS EXAMPLES:
- Memory Management Examples:
  - When user says: "I prefer window seats on flights" → add_memory_tool(user_id, "User prefers window seats on flights", contact_email)
  - Before recommending a restaurant → search_memory_tool(user_id, "food preferences and allergies")
  - When user says: "Remember that place I liked last time?" → search_memory_tool(user_id, "restaurant preferences and previous visits")

- Contact Management Examples:
  - When user says: "My friend Jane's email is jane@example.com" → add_contact_tool(user_id, "jane@example.com", "Jane")
  - When user provides new info: "Actually, Jane's last name is Smith" → First get_contacts_tool(user_id) to find Jane's UID, then update_contact_tool(user_id, contact_uid, last_name="Smith")
  - Before sending a message to someone → get_contacts_tool(user_id) to check if they exist in contacts

- Status Tracking Examples:
  - After user confirms booking → write_status_tool("whatsapp_agent", "assistant", conversation_id, "User confirmed hotel booking for July 15-20")
  - When resuming a conversation → read_status_tool(conversation_id) to check what was previously discussed
  - When handing off to another system → write_status_tool("whatsapp_agent", "assistant", conversation_id, "Waiting for payment confirmation from payment system")

- Document Management Examples:
  - After finding restaurant menu → store_documents_tool("menus", ["Full menu: Appetizers: Spring rolls $8, Salads: Caesar $10..."], metadata='{{"restaurant":"Thai Palace", "cuisine":"Thai"}}')
  - When user asks about a restaurant → search_documents_tool("menus", "Thai restaurant options", metadata_filter='{{"cuisine":"Thai"}}')
  - After confirming flight booking → store_documents_tool("travel_itineraries", ["Flight: AA123, Departure: JFK 10:00 AM, Arrival: LAX 1:30 PM"], metadata='{{"user_id":"' + user_id + '", "trip_date":"2023-07-15"}}')

IMPORTANT: Always pass the user_id parameter to global tools that require it (contact_management, memory_tools, etc.)
IMPORTANT: Always pass the conversation_id parameter to tools that track conversation state (status_tools, etc.)

USER AND CONVERSATION CONTEXT:
- You have been provided with user_id: {user_id if user_id else "None"} 
- You have been provided with conversation_id: {conversation_id if conversation_id else "None"}
- Use these IDs consistently when calling global tools to maintain context and continuity
- If user_id is provided, always use it for user-specific operations
- If conversation_id is provided, always use it for conversation-specific operations

CONVERSATION FLOW MANAGEMENT:
- After sending a message that requires a response, always check if you need to wait for a reply
- Use "SLEEP" to wait for responses instead of immediately proceeding
- When you wake up from sleep, check for new messages using get_last_interaction or list_messages
- Only proceed to the next step after receiving and processing the expected response
- Track conversation timing: if you just sent a message, you should usually wait before checking for responses
- Don't assume responses exist - always verify by checking recent messages after sleeping
- If the response came in the chat before you sent your first message then you should disregard it as it is not a response to your message - it was from another task.

SLEEP MODE USAGE:
- Use "SLEEP" when you're waiting for user responses, external events, or scheduled tasks

RESPONSE VERIFICATION:
- When checking for responses, compare timestamps to ensure messages are newer than your last sent message
- Look for messages that directly address your question or request
- If no relevant response is found, you may need to sleep again or send a follow-up

Current iteration: {iterations + 1}/{max_iterations}
"""
        
        # Prepare messages for the LLM
        # If first iteration, add system message
        llm_messages = []
        if iterations == 0:
            llm_messages.append(SystemMessage(content=system_message))
        
        # Add all previous messages
        for msg in messages:
            if isinstance(msg, ToolMessage) and not isinstance(msg.content, str):
                # Create a new ToolMessage with string content
                new_msg = ToolMessage(
                    content=str(msg.content),
                    tool_call_id=msg.tool_call_id,
                    name=msg.name
                )
                llm_messages.append(new_msg)
            else:
                llm_messages.append(msg)
        
        # Get response from LLM
        try:
            response = self.llm.invoke(llm_messages)
            
            # Log the agent's reasoning
            execution_log.append({
                "timestamp": datetime.now().isoformat(),
                "type": "reasoning",
                "message": response.content,
                "iteration": iterations + 1
            })
            
            # Log tool calls if any
            if response.tool_calls:
                for tool_call in response.tool_calls:
                    execution_log.append({
                        "timestamp": datetime.now().isoformat(),
                        "type": "tool_call",
                        "tool_name": tool_call["name"],
                        "args": tool_call["args"],
                        "iteration": iterations + 1
                    })
            
            # Check if task is completed, failed, or should sleep
            task_completed = state["task_completed"]
            error = state.get("error")
            should_sleep = False
            waiting_for_response = state.get("waiting_for_response", False)
            sleep_count = state.get("sleep_count", 0)
            last_sent_message_time = state.get("last_sent_message_time")
            
            if "TASK COMPLETED" in response.content:
                task_completed = True
            elif "TASK FAILED" in response.content:
                task_completed = True
                error = response.content
            elif "SLEEP" in response.content:
                should_sleep = True
                sleep_count += 1
            
            # Track if we just sent a message that expects a response
            sent_message_expecting_response = False
            if response.tool_calls:
                for tool_call in response.tool_calls:
                    if tool_call["name"] == "send_message":
                        # Check if the message content suggests we're asking a question or expecting a response
                        message_content = tool_call["args"].get("message", "").lower()
                        if any(indicator in message_content for indicator in [
                            "?", "when", "what", "how", "where", "available", "let me know", 
                            "please", "confirm", "tell me", "are you"
                        ]):
                            sent_message_expecting_response = True
                            last_sent_message_time = datetime.now().isoformat()
                            waiting_for_response = True
                            sleep_count = 0  # Reset sleep count when sending new message
            
            # Update state
            return {
                **state,
                "messages": messages + [response],
                "iterations": iterations + 1,
                "execution_log": execution_log,
                "task_completed": task_completed,
                "error": error,
                "should_sleep": should_sleep,
                "last_sent_message_time": last_sent_message_time,
                "waiting_for_response": waiting_for_response,
                "sleep_count": sleep_count
            }
            
        except Exception as e:
            execution_log.append({
                "timestamp": datetime.now().isoformat(),
                "type": "error",
                "message": f"Error in agent reasoning: {str(e)}",
                "iteration": iterations + 1
            })
            return {
                **state,
                "task_completed": True,
                "error": f"Agent error: {str(e)}",
                "execution_log": execution_log
            }
    
    async def execute_task(self, task: str, user_id: Optional[str] = None, 
                         conversation_id: Optional[str] = None, max_iterations: int = 10,
                         sleep_duration: int = 30) -> Dict[str, Any]:
        """Execute a task using the agent"""
        initial_state = {
            "messages": [],
            "task": task,
            "user_id": user_id,
            "conversation_id": conversation_id,
            "iterations": 0,
            "max_iterations": max_iterations,
            "sleep_duration": sleep_duration,
            "should_sleep": False,
            "last_sent_message_time": None,
            "waiting_for_response": False,
            "sleep_count": 0,
            "execution_log": [{
                "timestamp": datetime.now().isoformat(),
                "type": "task_start",
                "message": f"Starting task: {task}",
                "user_id": user_id,
                "conversation_id": conversation_id
            }],
            "task_completed": False,
            "error": None
        }
        
        try:
            # Run the graph

            add_monitoring_log("DEBUG", f"User ID: {user_id}")
            add_monitoring_log("DEBUG", f"Conversation ID: {conversation_id}")

            final_state = await asyncio.get_event_loop().run_in_executor(
                None, self.graph.invoke, initial_state
            )
            
            # Log tool results from messages
            for msg in final_state.get("messages", []):
                if isinstance(msg, ToolMessage):
                    # Ensure tool message content is a string
                    content = msg.content
                    if not isinstance(content, str):
                        content = str(content)
                    
                    final_state["execution_log"].append({
                        "timestamp": datetime.now().isoformat(),
                        "type": "tool_result",
                        "tool_name": msg.name,
                        "result": content,
                        "iteration": final_state["iterations"]
                    })
            
            return final_state
            
        except Exception as e:
            return {
                **initial_state,
                "task_completed": True,
                "error": f"Graph execution error: {str(e)}",
                "execution_log": initial_state["execution_log"] + [{
                    "timestamp": datetime.now().isoformat(),
                    "type": "error",
                    "message": f"Graph execution error: {str(e)}"
                }]
            }

# Global agent instance
agent = None

@app.on_event("startup")
async def startup_event():
    """Initialize the agent on startup"""
    global agent, auto_fetch_task, processed_message_ids, monitoring_logs
    
    # Initialize MongoDB connection
    if mongo.init_mongodb():
        # Load existing data from MongoDB
        processed_ids = mongo.load_processed_messages_from_db()
        processed_message_ids = set(processed_ids)
        
        logs = mongo.load_monitoring_logs_from_db()
        if logs:
            monitoring_logs = logs
            
        add_monitoring_log("INFO", "MongoDB initialized and data loaded successfully")
    else:
        add_monitoring_log("ERROR", "Failed to initialize MongoDB - running in memory-only mode")

    # Start auto-fetch task
    auto_fetch_task = asyncio.create_task(auto_fetch_messages())
    
    agent = WhatsAppAgent()
    print("WhatsApp Agent initialized successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown"""
    # Close MongoDB connection
    mongo.close_mongodb()
    print("MongoDB connection closed")

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.post("/execute_task", response_model=TaskResponse)
async def execute_task(request: TaskRequest, background_tasks: BackgroundTasks):
    """Execute a WhatsApp task using the agent in fire-and-forget mode"""
    try:
        if not agent:
            raise HTTPException(status_code=500, detail="Agent not initialized")
        
        # Generate a task ID immediately
        task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create initial log entry
        initial_log = [{
            "timestamp": datetime.now().isoformat(),
            "type": "task_start",
            "message": f"Starting task: {request.task}",
            "user_id": request.user_id,
            "conversation_id": request.conversation_id
        }]
        
        # Store task in MongoDB if conversation_id is provided
        if request.conversation_id:
            mongo.save_task_to_db(
                conversation_id=request.conversation_id,
                task=request.task,
                metadata={
                    "user_id": request.user_id,
                    "model": request.model,
                    "max_iterations": request.max_iterations,
                    "sleep_duration": request.sleep_duration
                }
            )
        
        # Save initial task state to MongoDB
        mongo.save_processed_message_to_db(task_id, {
            "task": request.task,
            "user_id": request.user_id,
            "conversation_id": request.conversation_id,
            "model": request.model,
            "status": "running",
            "message": "Task started in background",
            "timestamp": datetime.now().isoformat()
        })
        
        # Add the task to background tasks
        background_tasks.add_task(
            run_task_in_background,
            task_id=task_id,
            task=request.task,
            user_id=request.user_id,
            conversation_id=request.conversation_id,
            model=request.model,
            max_iterations=request.max_iterations,
            sleep_duration=request.sleep_duration or 30
        )
        
        # Return immediate response
        return TaskResponse(
            status="ok",
            message="Task started in background",
            execution_log=initial_log,
            task_id=task_id,
            user_id=request.user_id,
            conversation_id=request.conversation_id
        )
        
    except Exception as e:
        return TaskResponse(
            status="failed",
            message=f"Error starting task: {str(e)}",
            execution_log=[{
                "timestamp": datetime.now().isoformat(),
                "type": "error",
                "message": f"API error: {str(e)}"
            }],
            user_id=request.user_id,
            conversation_id=request.conversation_id
        )

async def run_task_in_background(task_id: str, task: str, user_id: Optional[str] = None,
                               conversation_id: Optional[str] = None, model: str = "llama-3.3-70b-versatile",
                               max_iterations: int = 10, sleep_duration: int = 30):
    """Run a task in the background and update MongoDB with results"""
    try:
        # Create a new agent with the specified model if different from default
        task_agent = agent
        if model != "llama-3.3-70b-versatile":
            task_agent = WhatsAppAgent(model)
        
        # Execute the task
        result = await task_agent.execute_task(
            task=task,
            user_id=user_id,
            conversation_id=conversation_id,
            max_iterations=max_iterations,
            sleep_duration=sleep_duration
        )
        
        # Determine final status
        if result["error"]:
            status = "failed"
            message = result["error"]
        elif result["task_completed"]:
            status = "ok"
            message = "Task completed successfully"
        else:
            status = "failed"
            message = "Task did not complete"
        
        # Update task execution in MongoDB with final results
        mongo.save_processed_message_to_db(task_id, {
            "task": task,
            "user_id": user_id,
            "conversation_id": conversation_id,
            "model": model,
            "status": status,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "completed_at": datetime.now().isoformat(),
            "execution_log": result["execution_log"]
        })
        
        add_monitoring_log("INFO", f"Background task {task_id} completed with status: {status}")
        
    except Exception as e:
        # Log the error and update MongoDB
        error_message = f"Background task error: {str(e)}"
        add_monitoring_log("ERROR", error_message)
        
        mongo.save_processed_message_to_db(task_id, {
            "task": task,
            "user_id": user_id,
            "conversation_id": conversation_id,
            "model": model,
            "status": "failed",
            "message": error_message,
            "timestamp": datetime.now().isoformat(),
            "completed_at": datetime.now().isoformat(),
            "execution_log": [{
                "timestamp": datetime.now().isoformat(),
                "type": "error",
                "message": error_message
            }]
        })

# Add a new endpoint to check task status
@app.get("/task_status/{task_id}", response_model=TaskResponse)
async def get_task_status(task_id: str):
    """Get the status of a background task by ID"""
    try:
        # Retrieve task data from MongoDB
        task_data = mongo.get_processed_message_from_db(task_id)
        
        if not task_data:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
        
        # Extract relevant fields
        status = task_data.get("status", "unknown")
        message = task_data.get("message", "No message available")
        execution_log = task_data.get("execution_log", [])
        user_id = task_data.get("user_id")
        conversation_id = task_data.get("conversation_id")
        
        return TaskResponse(
            status=status,
            message=message,
            execution_log=execution_log,
            task_id=task_id,
            user_id=user_id,
            conversation_id=conversation_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving task status: {str(e)}")

@app.get("/tools")
async def get_tools():
    """Get list of available WhatsApp and Global tools"""
    all_tools = get_whatsapp_tools() + get_global_tools()
    return {
        "whatsapp_tools": [
            {
                "name": tool.name,
                "description": tool.description,
                "args_schema": tool.args_schema.model_json_schema() if tool.args_schema else None
            }
            for tool in get_whatsapp_tools()
        ],
        "global_tools": [
            {
                "name": tool.name,
                "description": tool.description,
                "args_schema": tool.args_schema.model_json_schema() if tool.args_schema else None
            }
            for tool in get_global_tools()
        ],
        "total_tools": len(all_tools)
    }

@app.get("/models")
async def get_models():
    """Get list of available Groq models"""
    return {
        "models": [
            {
                "name": "llama-3.3-70b-versatile",
                "description": "Llama 3.3 70B - Most capable model, good for complex tasks"
            },
            {
                "name": "llama-3.1-70b-versatile",
                "description": "Llama 3.1 70B - High performance model"
            },
            {
                "name": "llama-3.1-8b-instant",
                "description": "Llama 3.1 8B - Fast and efficient for simple tasks"
            },
            {
                "name": "mixtral-8x7b-32768",
                "description": "Mixtral 8x7B - Good balance of speed and capability"
            },
            {
                "name": "gemma2-9b-it",
                "description": "Gemma 2 9B - Google's efficient model"
            }
        ]
    }

def add_monitoring_log(log_type: str, message: str, details: Dict[str, Any] = None):
    """Add a log entry for monitoring activities"""
    global monitoring_logs
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "type": log_type,
        "message": message,
        "details": details or {}
    }
    
    # Save to memory for quick access
    monitoring_logs.append(log_entry)
    
    # Keep only the last 1000 log entries in memory
    if len(monitoring_logs) > 1000:
        monitoring_logs = monitoring_logs[-1000:]
    
    # Save to MongoDB for persistence
    mongo.save_monitoring_log_to_db(log_type, message, details)
    
    print(f"[{log_type.upper()}] {message}")

def mark_message_as_processed(msg_id: str, msg_data: Dict[str, Any] = None):
    """Mark a message as processed"""
    global processed_message_ids
    
    # Add to in-memory set
    processed_message_ids.add(msg_id)
    
    # Keep the set size manageable in memory
    if len(processed_message_ids) > 10000:
        # Convert to list, keep the most recent 5000 entries, and convert back to set
        processed_message_ids = set(list(processed_message_ids)[-5000:])
    
    # Ensure msg_data is a dictionary to avoid errors
    if msg_data is None:
        msg_data = {}
    
    # Add chat_type field if not present
    if msg_data and 'chat_jid' in msg_data and 'chat_type' not in msg_data:
        chat_jid = msg_data.get('chat_jid', '')
        msg_data['chat_type'] = "group" if chat_jid and "@g.us" in chat_jid else "direct"
    
    # Add processed_at timestamp
    msg_data['processed_at'] = datetime.now().isoformat()
    
    # Save to MongoDB for persistence
    print(f"Marking message as processed: {msg_id}")
    mongo.save_processed_message_to_db(msg_id, msg_data)

def is_message_processed(msg_id: str) -> bool:
    """Check if a message has already been processed"""
    global processed_message_ids
    
    # First check in memory for speed
    if msg_id in processed_message_ids:
        return True
    
    # If not in memory, check MongoDB (might be from previous session)
    if mongo.is_message_processed_in_db(msg_id):
        # Add to memory cache for future quick access
        processed_message_ids.add(msg_id)
        return True
    
    return False

def generate_message_id(msg_data: Dict[str, Any]) -> str:
    """Generate a consistent message ID from message data"""
    # If the message already has an ID, use it
    if msg_data.get('id'):
        return msg_data['id']
    
    # Otherwise, generate an ID based on available fields
    sender = msg_data.get('sender', '')
    chat_name = msg_data.get('chat_name', '')
    chat_jid = msg_data.get('chat_jid', '')
    content = msg_data.get('content', '')
    timestamp = msg_data.get('timestamp', datetime.now().isoformat())
    
    # Create a content hash to help with deduplication
    import hashlib
    content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
    
    # Use chat_jid if available, otherwise use chat_name
    chat_identifier = chat_jid if chat_jid else chat_name
    
    # Generate ID with format: sender_chat_identifier_contenthash_timestamp
    return f"{sender}_{chat_identifier}_{content_hash}_{timestamp}"

async def process_new_message(msg_data: Dict[str, Any]):
    """Process a new incoming message and respond if needed"""
    try:
        # Extract message details
        msg_id = msg_data.get('id', '')
        sender = msg_data.get('sender', '')
        content = msg_data.get('content', '')
        chat_jid = msg_data.get('chat_jid', '')
        chat_name = msg_data.get('chat_name', '')
        is_from_me = msg_data.get('is_from_me', False)
        timestamp_str = msg_data.get('timestamp')
        
        # Generate a consistent message ID if one doesn't exist
        if not msg_id:
            msg_id = generate_message_id(msg_data)
            msg_data['id'] = msg_id

        # Skip messages older than 60 seconds
        if timestamp_str:
            try:
                msg_time = datetime.fromisoformat(timestamp_str)
                time_diff = (datetime.now() - msg_time).total_seconds()
                if time_diff > 60:
                    add_monitoring_log("INFO", f"Skipping old message received at {timestamp_str} ({time_diff:.1f} seconds old)", {"message_id": msg_id})
                    mark_message_as_processed(msg_id, msg_data)  # Mark it as processed so we don't check it again
                    return
            except Exception as e:
                add_monitoring_log("WARNING", f"Failed to parse timestamp {timestamp_str}: {str(e)}")
        
        # Skip our own messages
        if is_from_me:
            add_monitoring_log("DEBUG", f"Skipping own message: {content[:50]}...")
            mark_message_as_processed(msg_id, msg_data)  # Mark it as processed so we don't check it again
            return
        
        # Determine if message is from a group
        is_group = chat_jid and "@g.us" in chat_jid
        chat_type = "group" if is_group else "direct"
        
        # Log the new message
        add_monitoring_log("INFO", f"New message from {sender} in {chat_name} ({chat_type}): {content[:50]}...",
                         {"message_id": msg_id, "chat": chat_name, "chat_type": chat_type})
        
        # Create a task for the agent to respond to the message
        recipient = chat_jid if is_group else sender
        
        # Get conversation context
        try:
            # Get conversation context using the get_message_context tool
            from whatsapp_tools import get_whatsapp_tools
            tools = get_whatsapp_tools()
            get_context_tool = next((tool for tool in tools if tool.name == "get_message_context"), None)
            
            conversation_context = ""
            if get_context_tool and msg_id:
                # Get context around this message
                try:
                    add_monitoring_log("DEBUG", f"Getting context for message {msg_id}")
                    context_result = get_context_tool._run(
                        message_id=msg_id,
                        before=5,
                        after=0
                    )
                    
                    if context_result:
                        if isinstance(context_result, str):
                            conversation_context = f"Previous conversation context:\n{context_result}\n\n"
                            add_monitoring_log("DEBUG", f"Got string context: {len(conversation_context)} chars")
                        elif isinstance(context_result, list):
                            context_messages = [f"{m.get('sender', 'Unknown')}: {m.get('content', '')}" 
                                              for m in context_result if isinstance(m, dict)]
                            conversation_context = f"Previous conversation context:\n{chr(10).join(context_messages)}\n\n"
                            add_monitoring_log("DEBUG", f"Got list context with {len(context_result)} messages")
                except Exception as e:
                    add_monitoring_log("WARNING", f"Error getting message context: {str(e)}")
        except Exception as e:
            add_monitoring_log("WARNING", f"Failed to get message context: {str(e)}")
            conversation_context = ""
        
        # Get original task for this conversation if available
        original_task_context = ""
        if chat_jid:
            original_task_data = mongo.get_task_by_conversation_id(chat_jid)
            if original_task_data and original_task_data.get('task'):
                original_task = original_task_data['task']
                original_task_context = f"ORIGINAL TASK: {original_task}\n\n"
                add_monitoring_log("DEBUG", f"Retrieved original task for conversation {chat_jid}")
            else:
                add_monitoring_log("DEBUG", f"No original task found for conversation {chat_jid}")
        
        # Create a response task
        response_task = f"""
You are a Prosusware WhatsApp agent that helps people book travel trips and order food. Right now you already have been assigned a task and you have already reached out to the user about collecting some data.

{original_task_context}Your job is to respond to the message. First of all you should use tools to check the previous messages to see what you need.

If the user has answered the question. Confirm that is what you have received it. If not or if it is unclear then you should ask follow up questions.
YOU SHOULD ALWAYS SEND A MESSAGE - EVEN IF IT IS JUST TO SAY NOTED

{conversation_context}You received this message from {sender} in {"group" if is_group else "direct"} chat '{chat_name}': "{content}"

Please respond appropriately to this message. Keep your response natural, helpful, and concise.
After generating your response, send it back using the send_message tool.

IMPORTANT: This message was received in a {"GROUP" if is_group else "DIRECT"} chat.
{"When responding, you MUST send your response to the GROUP chat using the chat JID as recipient." if is_group else "Send your response directly to the sender."}

The recipient should be: {recipient}

Here are the tools you can use to help you complete this task:

You have access to these WhatsApp tools:
- list_messages: Get messages with filters and context
- list_chats: List available chats
- get_chat: Get chat information by JID
- get_direct_chat_by_contact: Find direct chat with a contact
- get_contact_chats: List all chats involving a contact
- get_last_interaction: Get most recent message with a contact
- get_message_context: Get context around a specific message (use this to understand conversation history)
- send_message: Send a message to a contact or group - 
- send_file: Send a file (image, video, document)
- send_audio_message: Send an audio message
- download_media: Download media from a message

You also have access to these Global Tools:
- web_search: Use for real-time information about travel destinations, restaurants, flight details, or current events. Particularly useful when you need up-to-date information not in your training data.
- Contact Management:
  - add_contact_tool: Create a new contact when a user mentions someone new they want to interact with. Only email is required, but collect as much information as available.
  - update_contact_tool: Update contact details when users provide new information about themselves or others.
  - get_contacts_tool: Check if a contact already exists before creating a new one, or to get a comprehensive view of a user's network. If this tool does not work then should use the list chats whatsapp tool instead.
- Memory Management:
  - add_memory_tool: IMPORTANT - Store any significant user preferences, requirements, or personal details shared during conversations. Examples: food allergies, travel preferences, important dates, family information, previous orders, etc.
  - search_memory_tool: ALWAYS search memories before making recommendations or when starting a new conversation with a returning user. This provides personalized context for better service.
- Status Tracking:
  - write_status_tool: Record important milestones in conversations (e.g., "User confirmed booking", "Waiting for payment details") to maintain state across sessions.
  - read_status_tool: Check previous conversation status before continuing a task that might have been interrupted.
- Document Management:
  - store_documents_tool: Save important structured information like menus, travel itineraries, booking confirmations, or receipts for later reference.
  - search_documents_tool: Retrieve previously stored documents when needed for reference or to continue an interrupted task.

IMPORTANT RULES:
1. Use phone numbers with country code but no + symbol (e.g., 447865463524)
2. For groups, use the whatsappJID format (e.g., <number>@g.us)
3. Be thorough in your approach - gather information before acting
4. When responding to messages, always use get_message_context to understand the conversation history
5. Consider previous conversation context when generating responses
6. CRITICAL: For GROUP chats, ALWAYS send responses to the GROUP chat using the chat JID as recipient
7. For DIRECT chats, send responses directly to the sender
8. If you need to wait or don't have anything to do right now, respond with "SLEEP" to enter sleep mode
9. Only EVER send one message per person.
10. NEVER send an identical message to the person you just sent a message to.

WHEN TO USE MEMORY TOOLS:
- ALWAYS add memories when users share:
  - Personal preferences (favorite foods, travel destinations, etc.)
  - Requirements or restrictions (dietary needs, accessibility requirements)
  - Important dates (birthdays, anniversaries, travel dates)
  - Contact details (phone numbers, addresses)
  - Feedback about previous experiences
- ALWAYS search memories:
  - At the beginning of conversations with returning users
  - Before making recommendations
  - When users reference previous interactions
  - When planning complex tasks like travel itineraries

GLOBAL TOOLS EXAMPLES:
- Memory Management Examples:
  - When user says: "I prefer window seats on flights" → add_memory_tool(user_id, "User prefers window seats on flights", contact_email)
  - Before recommending a restaurant → search_memory_tool(user_id, "food preferences and allergies")
  - When user says: "Remember that place I liked last time?" → search_memory_tool(user_id, "restaurant preferences and previous visits")

- Contact Management Examples:
  - When user says: "My friend Jane's email is jane@example.com" → add_contact_tool(user_id, "jane@example.com", "Jane")
  - When user provides new info: "Actually, Jane's last name is Smith" → First get_contacts_tool(user_id) to find Jane's UID, then update_contact_tool(user_id, contact_uid, last_name="Smith")
  - Before sending a message to someone → get_contacts_tool(user_id) to check if they exist in contacts

- Status Tracking Examples:
  - After user confirms booking → write_status_tool("whatsapp_agent", "assistant", conversation_id, "User confirmed hotel booking for July 15-20")
  - When resuming a conversation → read_status_tool(conversation_id) to check what was previously discussed
  - When handing off to another system → write_status_tool("whatsapp_agent", "assistant", conversation_id, "Waiting for payment confirmation from payment system")

- Document Management Examples:
  - After finding restaurant menu → store_documents_tool("menus", ["Full menu: Appetizers: Spring rolls $8, Salads: Caesar $10..."], metadata='{{"restaurant":"Thai Palace", "cuisine":"Thai"}}')
  - When user asks about a restaurant → search_documents_tool("menus", "Thai restaurant options", metadata_filter='{{"cuisine":"Thai"}}')
  - After confirming flight booking → store_documents_tool("travel_itineraries", ["Flight: AA123, Departure: JFK 10:00 AM, Arrival: LAX 1:30 PM"], metadata='{{"user_id":"' + user_id + '", "trip_date":"2023-07-15"}}')

IMPORTANT: Always pass the user_id parameter to global tools that require it (contact_management, memory_tools, etc.)
IMPORTANT: Always pass the conversation_id parameter to tools that track conversation state (status_tools, etc.)

USER AND CONVERSATION CONTEXT:
- Use the user_id and conversation_id consistently when calling global tools to maintain context and continuity
- If user_id is provided, always use it for user-specific operations
- If conversation_id is provided, always use it for conversation-specific operations

CONVERSATION FLOW MANAGEMENT:
- After sending a message that requires a response, always check if you need to wait for a reply
- Use "SLEEP" to wait for responses instead of immediately proceeding
- When you wake up from sleep, check for new messages using get_last_interaction or list_messages
- Only proceed to the next step after receiving and processing the expected response
- Track conversation timing: if you just sent a message, you should usually wait before checking for responses
- Don't assume responses exist - always verify by checking recent messages after sleeping
- If the response came in the chat before you sent your first message then you should disregard it as it is not a response to your message - it was from another task.

SLEEP MODE USAGE:
- Use "SLEEP" when you're waiting for user responses, external events, or scheduled tasks

RESPONSE VERIFICATION:
- When checking for responses, compare timestamps to ensure messages are newer than your last sent message
- Look for messages that directly address your question or request
- If no relevant response is found, you may need to sleep again or send a follow-up
"""
        
        add_monitoring_log("DEBUG", f"Executing response task for message {msg_id}")
        
        # Execute the response task
        result = await agent.execute_task(
            task=response_task,
            user_id=sender,
            conversation_id=chat_jid,
            max_iterations=3  # Keep it simple for auto-responses
        )
        
        # Check if a message was actually sent by examining the execution log
        message_sent = False
        sent_to = None
        sent_content = None
        
        for log_entry in result.get("execution_log", []):
            if log_entry.get("type") == "tool_call" and log_entry.get("tool_name") == "send_message":
                args = log_entry.get("args", {})
                sent_to = args.get("recipient", "unknown")
                sent_content = args.get("message", "")
                message_sent = True
                add_monitoring_log("DEBUG", f"Found send_message tool call to {sent_to}")
                break
        
        if message_sent and sent_to and sent_content:
            add_monitoring_log("SUCCESS", f"Successfully sent response to {sent_to}: {sent_content[:50]}...")
        else:
            add_monitoring_log("WARNING", f"No message was sent in response to {msg_id}")
            
        # Mark message as processed after we've handled it
        mark_message_as_processed(msg_id, msg_data)
            
    except Exception as e:
        add_monitoring_log("ERROR", f"Error processing message: {str(e)}")
        # Still mark as processed to avoid retrying a problematic message
        if 'msg_id' in locals() and 'msg_data' in locals():
            mark_message_as_processed(msg_id, msg_data)

async def auto_fetch_messages():
    """Background task to automatically fetch and reply to recent messages"""
    try:
        add_monitoring_log("INFO", "Auto-fetch messages started")
        
        while True:
            try:
                # Use the new approach to fetch unresponded messages
                await fetch_and_reply_unresponded(limit=50)
                
                # Wait 10 seconds before checking again (longer interval since we're not using time windows)
                await asyncio.sleep(10)
                
            except Exception as e:
                add_monitoring_log("ERROR", f"Error in auto-fetch loop: {str(e)}")
                await asyncio.sleep(10)  # Wait before retrying
                
    except asyncio.CancelledError:
        add_monitoring_log("INFO", "Auto-fetch messages stopped")
    except Exception as e:
        add_monitoring_log("ERROR", f"Fatal error in auto-fetch: {str(e)}")

async def fetch_and_reply_unresponded(limit: int = 50):
    """Fetch recent messages and reply to ones we haven't responded to yet"""
    try:
        if not agent:
            raise HTTPException(status_code=500, detail="Agent not initialized")
        
        # Use the list_messages tool directly to get recent messages (without time filtering)
        from whatsapp_tools import get_whatsapp_tools
        tools = get_whatsapp_tools()
        list_messages_tool = next((tool for tool in tools if tool.name == "list_messages"), None)
        
        if not list_messages_tool:
            return TaskResponse(
                status="failed",
                message="list_messages tool not found",
                execution_log=[{
                    "timestamp": datetime.now().isoformat(),
                    "type": "error",
                    "message": "list_messages tool not found"
                }]
            )
        
        # Get recent messages without time filtering
        messages = list_messages_tool._run(
            limit=limit,  # Get up to X recent messages
            include_context=False  # Don't include context for initial fetch
        )
        
        execution_log = [{
            "timestamp": datetime.now().isoformat(),
            "type": "info",
            "message": f"Fetched {limit} most recent messages"
        }]
        
        new_messages_count = 0
        processed_messages_count = 0
        
        # Process messages
        if isinstance(messages, list):
            execution_log.append({
                "timestamp": datetime.now().isoformat(),
                "type": "info",
                "message": f"Found {len(messages)} messages"
            })
            
            for msg in messages:
                if isinstance(msg, dict):
                    # Generate message ID for this message
                    msg_id = msg.get('id', '') or generate_message_id(msg)
                    msg['id'] = msg_id
                    
                    # Check if we've already processed this message
                    if not is_message_processed(msg_id):
                        # Process each new message individually
                        await process_new_message(msg)
                        new_messages_count += 1
                    else:
                        processed_messages_count += 1
                        
        elif isinstance(messages, str) and "No messages to display" not in messages:
            # Parse the string response into message objects
            message_lines = messages.strip().split('\n')
            
            for line in message_lines:
                # Skip empty lines or lines without expected format
                if not line.strip() or "Chat:" not in line or "From:" not in line:
                    continue
                    
                try:
                    # Extract timestamp if available
                    timestamp = datetime.now().isoformat()
                    if line.startswith("[") and "]" in line:
                        timestamp_str = line[1:line.find("]")]
                        try:
                            timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S").isoformat()
                        except:
                            pass  # Use default timestamp if parsing fails
                    
                    # Extract chat info
                    chat_parts = line.split("Chat:")
                    if len(chat_parts) < 2:
                        continue
                        
                    from_parts = chat_parts[1].split("From:")
                    if len(from_parts) < 2:
                        continue
                        
                    chat_name = from_parts[0].strip()
                    
                    # Find the first colon after "From:" to separate sender and content
                    after_from = from_parts[1]
                    colon_index = after_from.find(":")
                    
                    if colon_index == -1:
                        continue  # No content separator found
                        
                    sender = after_from[:colon_index].strip()
                    content = after_from[colon_index+1:].strip()
                    
                    # Create a message object
                    msg_obj = {
                        'sender': sender,
                        'content': content,
                        'chat_jid': chat_name,  # Using chat name as JID
                        'chat_name': chat_name,
                        'is_from_me': False,  # Assume not from me
                        'timestamp': timestamp
                    }
                    
                    # Generate a message ID using our improved function
                    msg_obj['id'] = generate_message_id(msg_obj)
                    
                    # Check if we've already processed this message
                    if not is_message_processed(msg_obj['id']):
                        # Process this message
                        await process_new_message(msg_obj)
                        new_messages_count += 1
                    else:
                        processed_messages_count += 1
                        
                except Exception as e:
                    execution_log.append({
                        "timestamp": datetime.now().isoformat(),
                        "type": "error",
                        "message": f"Failed to parse message: {str(e)}"
                    })
            
        execution_log.append({
            "timestamp": datetime.now().isoformat(),
            "type": "info",
            "message": f"Processed {new_messages_count} new messages, skipped {processed_messages_count} already processed messages"
        })
        
        return TaskResponse(
            status="ok",
            message=f"Processed {new_messages_count} new messages successfully",
            execution_log=execution_log,
            task_id=f"unresponded_msgs_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        
    except Exception as e:
        return TaskResponse(
            status="failed",
            message=f"Error processing unresponded messages: {str(e)}",
            execution_log=[{
                "timestamp": datetime.now().isoformat(),
                "type": "error",
                "message": f"API error: {str(e)}"
            }]
        )

@app.get("/auto_fetch_status")
async def get_auto_fetch_status():
    """Get the current status of auto-fetch"""
    global auto_fetch_task
    
    is_running = auto_fetch_task is not None and not auto_fetch_task.done()
    
    return {
        "running": is_running,
        "message": "Auto-fetch is running" if is_running else "Auto-fetch is not running"
    }