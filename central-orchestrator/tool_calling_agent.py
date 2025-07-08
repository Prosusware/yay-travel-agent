import os
import json
import time
import requests
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime

try:
    from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_google_genai import ChatGoogleGenerativeAI
    LANGCHAIN_AVAILABLE = True
except ImportError:
    print("⚠️ LangChain modules not available, using standalone mode")
    LANGCHAIN_AVAILABLE = False

try:
    from tavily import TavilyClient
    TAVILY_AVAILABLE = True
except ImportError:
    print("⚠️ Tavily not available, web search will be limited")
    TAVILY_AVAILABLE = False

from utils import tool_wrapper
from phone_agent import extract_phone_numbers_from_text, format_phone_number_international
from global_tools import (
    global_web_search,
    add_contact,
    update_contact,
    get_contacts,
    get_user,
    add_memory,
    search_memory,
    write_status,
    read_status
)
from serp_tools import serp_search, flights, hotels, maps, amazon
from whatsapp_agent import execute_whatsapp_task
from checkout_agent import book_flight


# Initialize clients
if TAVILY_AVAILABLE:
    tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
else:
    tavily_client = None

if LANGCHAIN_AVAILABLE:
    gemini_llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-pro-preview-06-05",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.5
    )
else:
    # Simple fallback for when LangChain is not available
    gemini_llm = None
    print("⚠️ Gemini LLM not available, some features will be limited")


@tool_wrapper
def web_search(query: str, max_results: int = 10, search_depth: str = "advanced") -> Dict[str, Any]:
    """
    Search the web using Tavily API to find information relevant to the current task.
    
    Args:
        query: The search query
        max_results: Maximum number of results to return (default: 10)
        search_depth: Search depth - "basic" or "advanced" (default: "advanced")
        
    Returns:
        Dictionary containing search results and metadata
    """
    try:
        if not TAVILY_AVAILABLE:
            return {
                "success": False,
                "error": "Tavily not available",
                "query": query,
                "results": [],
                "result_count": 0,
                "phone_numbers_found": [],
                "timestamp": datetime.now().isoformat(),
                "search_depth": search_depth
            }
        
        print(f"🔍 Searching the web for: {query}")
        
        response = tavily_client.search(
            query=query,
            max_results=max_results,
            search_depth=search_depth,
            include_answer=True,
            include_images=False
        )
        
        # Process and enhance results
        processed_results = []
        phone_numbers_found = []
        
        for result in response.get("results", []):
            processed_result = {
                "title": result.get("title", ""),
                "content": result.get("content", ""),
                "url": result.get("url", ""),
                "score": result.get("score", 0),
                "relevance": "high" if result.get("score", 0) > 0.8 else "medium" if result.get("score", 0) > 0.5 else "low"
            }
            processed_results.append(processed_result)
            
            # Extract phone numbers from content
            content = result.get("content", "") + " " + result.get("title", "")
            found_phones = extract_phone_numbers_from_text(content)
            for phone in found_phones:
                phone["source"] = result.get("title", "")
                phone["url"] = result.get("url", "")
                phone_numbers_found.append(phone)
        
        search_result = {
            "success": True,
            "query": query,
            "answer": response.get("answer", ""),
            "results": processed_results,
            "result_count": len(processed_results),
            "phone_numbers_found": phone_numbers_found,
            "timestamp": datetime.now().isoformat(),
            "search_depth": search_depth
        }
        
        print(f"✅ Found {len(processed_results)} results")
        if phone_numbers_found:
            print(f"📞 Found {len(phone_numbers_found)} phone numbers")
        
        return search_result
        
    except Exception as e:
        print(f"❌ Search failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "query": query,
            "timestamp": datetime.now().isoformat()
        }


@tool_wrapper
def make_outbound_call(task: str, phone_number: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Makes a complete outbound phone call to perform a task. 
    This tool handles generating the call script and interacting with the phone call API.
    The conversation_id is handled automatically by the agent.

    Args:
        task: A detailed description of the task to be accomplished during the call.
        phone_number: The phone number to call in international format.

    Returns:
        A dictionary with the call status: {"success": True/False, "message": "...", "call_id": "..."}
    """
    try:
        print(f"📞 Initiating outbound call for task: {task}")
        print(f"📱 Calling: {phone_number}")

        # 1. Format phone number
        formatted_phone = format_phone_number_international(phone_number)
        print(f"📱 Formatted phone: {formatted_phone}")

        # 2. Generate phone call content
        if not LANGCHAIN_AVAILABLE or not gemini_llm:
             raise Exception("LangChain or Gemini LLM not available to generate call content.")

        print("\n🤖 Generating task-specific call content...")
        
        task_content_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert at generating task-specific content for phone calls. Based on the task, generate a task-specific section that will be inserted into a system prompt template.

The task-specific section should:
- Clearly explain what needs to be accomplished
- Specify the desired outcome
- Be concise but complete (2-3 sentences max)

IMPORTANT: You MUST respond with ONLY the task-specific content text. Do not include any JSON formatting or extra text."""),
                ("user", """Task: {task}
Context: No additional context available

Generate the task-specific section for this call.""")
        ])
    
        chain = task_content_prompt | gemini_llm
        response = chain.invoke({"task": task})
        task_section = response.content.strip()

        if not task_section or len(task_section) < 10:
            raise Exception("Generated task section is too short or empty.")

        conversation_id_section = f"\n\nCONVERSATION ID: {conversation_id}" if conversation_id else ""
        
        system_prompt = f"""You are a personal assistant called Magnus. You are making outbound calls on behalf of users. You are polite, efficient, and focused on completing tasks successfully.

CORE GUIDELINES:
- Always be assertive, direct and use colloquial language
- Listen actively and ask clarifying questions when needed
- Do not tell them you are making the call on behalf of a user, just focus on completing the task
- If the user provides insufficient information, infer or create the necessary details based on context and proceed. As long as the task is completed, it's up to you how this is achieved and you can decide the details yourself.

CURRENT TASK:
{task_section}

CONTEXT INFORMATION:
No additional context available{conversation_id_section}

Remember to be helpful and professional throughout the entire conversation. Focus on completing the task while maintaining a positive interaction."""

        first_message = "Hello!"
        print("✅ Call content generated.")

        # 3. Make the ElevenLabs call
        print(f"\n📞 Making ElevenLabs API call to {formatted_phone}...")
        endpoint_url = "https://api.elevenlabs.io/v1/convai/twilio/outbound-call"
        
        payload = {
            "agent_id": os.getenv("ELEVENLABS_AGENT_ID"),
            "agent_phone_number_id": os.getenv("ELEVENLABS_PHONE_NUMBER_ID"),
            "to_number": formatted_phone,
            "conversation_initiation_client_data": {
                "conversation_config_override": {
                    "agent": {
                        "prompt": {"prompt": system_prompt},
                        "first_message": first_message
                    }
                }
            }
        }
        
        headers = {
            "Xi-Api-Key": os.getenv("ELEVENLABS_API_KEY"),
            "Content-Type": "application/json",
            "User-Agent": "LangGraph-Agent/2.0"
        }
        
        response = requests.post(endpoint_url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            call_id = result.get("call_id")
            print(f"✅ Call initiated successfully - Call ID: {call_id}")
            return {
                "success": True,
                "message": f"ElevenLabs outbound call initiated successfully.",
                "call_id": call_id,
            }
        else:
            error_message = f"ElevenLabs API Error {response.status_code}: {response.text}"
            print(f"❌ {error_message}")
            return {
                "success": False,
                "message": error_message
            }

    except Exception as e:
        error_msg = f"Phone call tool failed: {str(e)}"
        print(f"❌ {error_msg}")
        return {
            "success": False,
            "message": error_msg,
        }


@tool_wrapper
def sleep_tool(duration_seconds: int = 60) -> Dict[str, Any]:
    """
    Sleep/wait for a specified duration. Useful for waiting between actions or giving time for processes to complete.
    
    Args:
        duration_seconds: Number of seconds to sleep (default: 60 seconds = 1 minute)
        
    Returns:
        Dictionary with sleep completion status
    """
    try:
        print(f"😴 Sleeping for {duration_seconds} seconds...")
        start_time = datetime.now()
        
        time.sleep(duration_seconds)
        
        end_time = datetime.now()
        actual_duration = (end_time - start_time).total_seconds()
        
        print(f"⏰ Sleep completed after {actual_duration:.1f} seconds")
        
        return {
            "success": True,
            "requested_duration": duration_seconds,
            "actual_duration": actual_duration,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "message": f"Successfully slept for {actual_duration:.1f} seconds"
        }
        
    except Exception as e:
        print(f"❌ Sleep tool failed: {str(e)}")
        return {
            "success": False,
            "error": f"Sleep tool error: {str(e)}",
            "requested_duration": duration_seconds,
            "timestamp": datetime.now().isoformat()
        }


@tool_wrapper
def mark_task_as_complete(justification: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Marks the current task as complete after verifying all steps are done. You MUST call this tool as the final step.

    Before calling this tool, you should have verified that the original request has been fully satisfied.
    The agent will exit after this tool is successfully called.

    Args:
        justification: A clear and concise explanation of why the task is considered complete.
        conversation_id: The conversation ID for status updates. This is injected automatically.

    Returns:
        A dictionary confirming the task has been marked as complete.
    """
    try:
        if not conversation_id:
             raise ValueError("conversation_id is required to mark task as complete.")

        print(f"✅ Task being marked as complete. Justification: {justification}")
        
        status_result = write_status(
            conversation_id=conversation_id,
            status=f"TASK_COMPLETED; Justification: {justification}"
        )
        
        if not status_result.get("success"):
            print(f"⚠️ Failed to write final status update: {status_result.get('error')}")
        
        return {
            "success": True,
            "message": "TASK_COMPLETED"
        }
        
    except Exception as e:
        print(f"❌ Error marking task as complete: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


# List of available tools
AVAILABLE_TOOLS = [
    web_search, 
    make_outbound_call, 
    sleep_tool,
    global_web_search,
    add_contact,
    update_contact,
    get_contacts,
    add_memory,
    search_memory,
    write_status,
    read_status,
    serp_search,
    flights,
    hotels,
    maps,
    amazon,
    execute_whatsapp_task,
    book_flight,
    mark_task_as_complete
]


class ToolCallingAgent:
    """
    A tool calling agent that can perform various tasks using available tools.
    """
    
    def __init__(self, user_id: str, max_iterations: int = 10):
        if not LANGCHAIN_AVAILABLE:
            raise ImportError("LangChain is required for the tool calling agent.")
        
        self.max_iterations = max_iterations
        self.user_id = user_id
        self.tools = {tool.name: tool for tool in AVAILABLE_TOOLS}
        self.system_prompt_template = self.create_system_prompt()

    def create_system_prompt(self) -> str:
        """Create the system prompt for the agent."""
        tool_descriptions = []
        for tool_func in self.tools.values():
            tool_descriptions.append(f"- {tool_func.name}: {tool_func.description}")
        
        return f"""You are an intelligent task completion agent. You can complete various tasks by calling the available tools.

AVAILABLE TOOLS:
{chr(10).join(tool_descriptions)}

GUIDELINES:
1. The user will provide an initial context object. Use this to inform your plan and actions.
2. Analyze the user's request and break it down into steps
3. IMPORTANT: Do NOT include `user_id` or `conversation_id` in your tool calls. The agent handles these automatically.
4. Use the appropriate tools to gather information and complete tasks
5. For phone calls, you may need to search for phone numbers first using web_search or get_contacts
6. Always provide clear updates on your progress using write_status
7. If you need to wait for something (like a call to complete), use the sleep_tool
8. Be methodical and thorough in your approach
9. Explain your reasoning for each tool call
10. Use the phone_agent or whatsapp_agent to get in touch with the user if you need their input
11. for the whatsapp_agent, include the phoneNumber of the person to contact in the task
12. Once you have verified that the task is complete, you MUST call `mark_task_as_complete` to finish.

TASK COMPLETION STRATEGY:
- For ordering/booking tasks: Search for contact info, then make phone call
- For information gathering: Use web_search or global_web_search for targeted queries
- For time-sensitive tasks: Use sleep_tool to wait when appropriate
- For phone calls: Ensure you have a valid phone number first
- For contact management: Use add_contact, update_contact, and get_contacts
- For memory: Use add_memory and search_memory to store and retrieve information
- Any phone_agent or whatsapp_agent will add additional information to memory and will provide status updates which you can read with the relevant tools
- If you are missing the required info to complete the task and have created phone or whatsapp agents, then use your sleep tool to wait for the agents to complete their tasks and then check memory and status updates   

Remember to be helpful, efficient, and complete all requested tasks successfully."""

    def analyze_task_and_plan(self, task: str) -> List[str]:
        """
        Analyze the task and create a plan using Gemini AI.
        
        Args:
            task: The task description
            
        Returns:
            List of planned steps
        """
        if LANGCHAIN_AVAILABLE and gemini_llm:
            planning_prompt = ChatPromptTemplate.from_messages([
                ("system", """You are an expert task planner. Analyze the given task and create a step-by-step plan.

Available tools:
- web_search, global_web_search: Search the web for information
- make_outbound_call: Make phone calls to complete tasks
- sleep_tool: Wait/sleep for specified duration
- add_contact, update_contact, get_contacts: Manage contacts
- add_memory, search_memory: Store and retrieve memories
- write_status, read_status: Read and write status updates
- serp_search: Get search results from the SerpAPI Google Search API.
- flights: Get flight information from the SerpAPI Google Flights API.
- hotels: Get hotel information from the SerpAPI Google Hotels API.
- maps: Get map information from the SerpAPI Google Maps API.
- amazon: Get product information from the SerpAPI Amazon API.
- execute_whatsapp_task: Execute a task by contacting someone using the WhatsApp agent. Include the phone number of the recipient in the task.
- book_flight: Book a flight using the Checkout Agent API.
- mark_task_as_complete: Marks the current task as complete and exits the agent.

Return a JSON list of steps, where each step describes what needs to be done.

Example format:
["Search for restaurant contact information", "Call restaurant to place order", "Confirm order details"]

IMPORTANT: Return ONLY the JSON list, no other text."""),
                ("user", "Create a step-by-step plan for this task: {task}")
            ])
            
            try:
                chain = planning_prompt | gemini_llm
                response = chain.invoke({"task": task})
                
                # Parse the JSON response
                plan_text = response.content.strip()
                
                # Extract JSON from response
                import re
                json_match = re.search(r'\[.*\]', plan_text, re.DOTALL)
                if json_match:
                    plan = json.loads(json_match.group(0))
                else:
                    plan = json.loads(plan_text)
                
                return plan
                
            except Exception as e:
                print(f"⚠️ Gemini AI Planning failed: {e}")

    def run(self, task: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Run the agent to complete the given task.
        
        Args:
            task: The task to complete
            conversation_id: Optional conversation ID to pass to tools
            
        Returns:
            Dictionary with execution results
        """
        print(f"\n{'='*80}")
        print(f"🚀 TOOL CALLING AGENT STARTED")
        print(f"{'='*80}")
        print(f"📋 Task: {task}")
        print(f"👤 User ID: {self.user_id}")
        print(f"🆔 Conversation ID: {conversation_id or 'Not provided'}")
        print(f"{'='*80}")
        
        # Store task context
        context = {
            "original_task": task,
            "user_id": self.user_id,
            "conversation_id": conversation_id,
            "user_data": {},
            "plan": [],
            "search_results": [],
            "phone_calls": [],
            "found_phone_numbers": []
        }

        # Fetch user data at the start
        if self.user_id:
            print(f"👤 Fetching user data for {self.user_id}...")
            user_data = get_user(self.user_id)
            if "error" not in user_data:
                # Drop contacts from user data as they are handled separately
                if "Contacts" in user_data:
                    del user_data["Contacts"]
                context["user_data"] = user_data
                print("✅ User data loaded.")
            else:
                print(f"⚠️ Could not fetch user data: {user_data['error']}")
        
        # Create initial plan
        plan = self.analyze_task_and_plan(task)
        context["plan"] = plan
        print(f"📝 Initial Plan:")
        for i, step in enumerate(plan, 1):
            print(f"   {i}. {step}")
        
        # Initialize conversation and execution log
        initial_context_str = json.dumps(context)
        print(initial_context_str)
        self.conversation_history = [
            SystemMessage(content=self.system_prompt_template),
            HumanMessage(content=f"""Please complete the following task.

TASK:
{task}

INITIAL CONTEXT:
{initial_context_str}""")
        ]
        self.execution_log = []
        
        iteration = 0
        task_completed = False
        while iteration < self.max_iterations:
            iteration += 1
            print(f"\n{'='*60}")
            print(f"🔄 ITERATION {iteration}/{self.max_iterations}")
            print(f"{'='*60}")
            
            # Get response from LLM
            try:
                # Bind tools to the LLM
                llm_with_tools = gemini_llm.bind_tools(list(self.tools.values()))
                response = llm_with_tools.invoke(self.conversation_history)
                
                self.conversation_history.append(response)
                
                # Check if the LLM wants to use tools
                if response.tool_calls:
                    print(f"🛠️ Agent wants to use {len(response.tool_calls)} tool(s)")
                    
                    # Execute each tool call
                    for tool_call in response.tool_calls:
                        tool_name = tool_call["name"]
                        tool_args = tool_call["args"]
                        
                        print(f"\n🔧 Calling tool: {tool_name}")
                        print(f"📊 Arguments: {tool_args}")
                        
                        # Special handling for tools that need user_id or conversation_id
                        if tool_name in ["add_contact", "update_contact", "get_contacts", "add_memory", "search_memory", "execute_whatsapp_task"]:
                            tool_args["user_id"] = self.user_id
                        if tool_name in ["write_status", "read_status", "execute_whatsapp_task", "make_outbound_call", "book_flight", "mark_task_as_complete"]:
                            tool_args["conversation_id"] = conversation_id

                        if tool_name in self.tools:
                            # Execute the tool
                            try:
                                tool_result = self.tools[tool_name].invoke(tool_args)
                                
                                # Store results in context
                                if tool_name == "web_search":
                                    context["search_results"].append(tool_result)
                                    if tool_result.get("phone_numbers_found"):
                                        context["found_phone_numbers"].extend(tool_result["phone_numbers_found"])
                                elif tool_name == "make_outbound_call":
                                    context["phone_calls"].append(tool_result)
                                
                                # Add tool result to conversation
                                tool_message = ToolMessage(
                                    content=json.dumps(tool_result, indent=2),
                                    tool_call_id=tool_call["id"]
                                )
                                self.conversation_history.append(tool_message)
                                
                                # Log execution
                                self.execution_log.append({
                                    "iteration": iteration,
                                    "tool": tool_name,
                                    "args": tool_args,
                                    "result": tool_result,
                                    "timestamp": datetime.now().isoformat()
                                })
                                
                                print(f"✅ Tool execution completed")

                                if tool_name == 'mark_task_as_complete' and tool_result.get('success'):
                                    print("➡️ Task marked as complete. Agent will now exit.")
                                    task_completed = True
                                
                            except Exception as e:
                                error_msg = f"Tool execution failed: {str(e)}"
                                print(f"❌ {error_msg}")
                                
                                tool_message = ToolMessage(
                                    content=f"Error: {error_msg}",
                                    tool_call_id=tool_call["id"]
                                )
                                self.conversation_history.append(tool_message)
                        else:
                            error_msg = f"Unknown tool: {tool_name}"
                            print(f"❌ {error_msg}")
                            
                            tool_message = ToolMessage(
                                content=f"Error: {error_msg}",
                                tool_call_id=tool_call["id"]
                            )
                            self.conversation_history.append(tool_message)
                
                    if task_completed:
                        break
                else:
                    # No tool calls, check if task is complete
                    print("💬 Agent response (no tool calls):")
                    print(response.content)
                    
                    # Check if the agent thinks the task is complete
                    if any(phrase in response.content.lower() for phrase in [
                        "task completed", "successfully completed", "task is complete", 
                        "finished", "done", "accomplished"
                    ]):
                        print("✅ Agent indicates task completion")
                        break
                
            except Exception as e:
                print(f"❌ Iteration failed: {str(e)}")
                break
        
        # Prepare final results
        final_results = {
            "task": task,
            "user_id": self.user_id,
            "conversation_id": conversation_id,
            "iterations": iteration,
            "conversation_history": [msg.content if hasattr(msg, 'content') else str(msg) for msg in self.conversation_history],
            "execution_log": self.execution_log,
            "context": context,
            "final_response": self.conversation_history[-1].content if self.conversation_history else "No response",
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"\n{'='*80}")
        print(f"🏁 AGENT EXECUTION COMPLETED")
        print(f"{'='*80}")
        print(f"📊 Iterations: {iteration}/{self.max_iterations}")
        print(f"🔍 Searches performed: {len(context['search_results'])}")
        print(f"📞 Phone calls made: {len(context['phone_calls'])}")
        print(f"📱 Phone numbers found: {len(context['found_phone_numbers'])}")
        print(f"{'='*80}")
        
        return final_results


def run_tool_calling_agent(task: str, user_id: str, conversation_id: Optional[str] = None, max_iterations: int = 10) -> Dict[str, Any]:
    """
    Convenience function to run the tool calling agent.
    
    Args:
        task: The task to complete
        user_id: The user ID for context.
        conversation_id: Optional conversation ID to pass to tools
        max_iterations: Maximum number of iterations
        
    Returns:
        Agent execution results
    """
    if LANGCHAIN_AVAILABLE:
        agent = ToolCallingAgent(user_id=user_id, max_iterations=max_iterations)
        return agent.run(task, conversation_id=conversation_id)
    else:
        # Since we are removing the simple agent, we should raise an error if LangChain is not available.
        raise ImportError("LangChain is required to run the tool calling agent.") 