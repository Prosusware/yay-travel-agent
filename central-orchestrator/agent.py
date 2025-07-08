import os
import json
from typing import TypedDict, Annotated, List, Dict, Any, Optional
from datetime import datetime
import requests
from langgraph.graph import StateGraph, END, add_messages
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_mistralai import ChatMistralAI
from tavily import TavilyClient
import asyncio


# State definition
class AgentState(TypedDict):
    messages: Annotated[List, add_messages]
    current_task: str
    task_complete: bool
    completion_status: str
    missing_requirements: List[str]
    key_facts: Dict[str, Any]
    tavily_results: List[Dict[str, Any]]
    phone_call_results: List[Dict[str, Any]]
    step_count: int


# Initialize Tavily client
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# Initialize Mistral LLM
mistral_llm = ChatMistralAI(
    api_key=os.getenv("MISTRAL_API_KEY"),
    model=os.getenv("MISTRAL_MODEL", "mistral-large-latest"),
    temperature=0.1
)


@tool
def search_tavily(query: str, max_results: int = 5) -> Dict[str, Any]:
    """
    Search the web using Tavily API for relevant information.
    
    Args:
        query: The search query
        max_results: Maximum number of results to return
        
    Returns:
        Dictionary containing search results
    """
    try:
        response = tavily_client.search(
            query=query,
            max_results=max_results,
            search_depth="advanced"
        )
        return {
            "success": True,
            "query": query,
            "results": response.get("results", []),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "query": query,
            "timestamp": datetime.now().isoformat()
        }


@tool
def call_elevenlabs_outbound(task: str, phone_number: str, system_prompt: str = "", first_message: str = "") -> Dict[str, Any]:
    """
    Make an outbound phone call using ElevenLabs ConvAI API directly.
    
    Args:
        task: The task to be communicated/executed during the call (stored as context)
        phone_number: The phone number to call (international format, e.g., 447874943523)
        system_prompt: The system prompt/instructions for the ElevenLabs agent
        first_message: The first message the agent will say when the call connects
        
    Returns:
        Dictionary containing call result information
    """
    try:
        # ElevenLabs ConvAI outbound call endpoint
        endpoint_url = "https://api.elevenlabs.io/v1/convai/twilio/outbound-call"
        
        # Prepare payload for ElevenLabs API
        payload = {
            "agent_id": os.getenv("ELEVENLABS_AGENT_ID"),
            "agent_phone_number_id": os.getenv("ELEVENLABS_PHONE_NUMBER_ID"),
            "to_number": phone_number
        }
        
        # Add optional parameters using conversation_config_override structure
        if system_prompt or first_message:
            payload["conversation_initiation_client_data"] = {
                "conversation_config_override": {
                    "agent": {}
                }
            }
            
            if system_prompt:
                payload["conversation_initiation_client_data"]["conversation_config_override"]["agent"]["prompt"] = {
                    "prompt": system_prompt
                }
            
            if first_message:
                payload["conversation_initiation_client_data"]["conversation_config_override"]["agent"]["first_message"] = first_message
        
        # Set required headers
        headers = {
            "Xi-Api-Key": os.getenv("ELEVENLABS_API_KEY"),
            "Api-Key": "xi-api-key",
            "Content-Type": "application/json"
        }
        
        # Make the API call
        response = requests.post(endpoint_url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            return {
                "success": True,
                "call_id": result.get("call_id"),
                "conversation_id": result.get("conversation_id"),
                "task": task,
                "phone_number": phone_number,
                "status": result.get("status", "initiated"),
                "message": "ElevenLabs outbound call initiated successfully",
                "timestamp": datetime.now().isoformat(),
                "agent_id": os.getenv("ELEVENLABS_AGENT_ID"),
                "elevenlabs_response": result
            }
        else:
            return {
                "success": False,
                "error": f"ElevenLabs API Error {response.status_code}: {response.text}",
                "task": task,
                "phone_number": phone_number,
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Exception calling ElevenLabs API: {str(e)}",
            "task": task,
            "phone_number": phone_number,
            "timestamp": datetime.now().isoformat()
        }


def analyze_task_completion(state: AgentState) -> Dict[str, Any]:
    """
    Analyze if the current task is complete based on the state and results using Mistral inference.
    
    Args:
        state: Current agent state
        
    Returns:
        Dictionary with completion analysis
    """
    task = state.get("current_task", "")
    key_facts = state.get("key_facts", {})
    phone_results = state.get("phone_call_results", [])
    tavily_results = state.get("tavily_results", [])
    
    # Create context for Mistral
    context = {
        "task": task,
        "phone_calls_made": len(phone_results),
        "successful_calls": sum(1 for call in phone_results if call.get("success")),
        "research_results": len(tavily_results),
        "key_facts_count": len(key_facts),
        "latest_call_success": phone_results[-1].get("success") if phone_results else False,
        "has_research_data": bool(tavily_results and any(r.get("success") for r in tavily_results))
    }
    
    # Use Mistral to analyze completion
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an intelligent task completion analyzer. Analyze whether a given task has been completed based on the available information.

Task analysis criteria:
- Phone calls: Check if required calls were made successfully
- Research: Verify if necessary information was gathered
- Key facts: Ensure important information was documented

IMPORTANT: You MUST respond with ONLY valid JSON in this exact format. Do not include any other text:
{{
    "is_complete": true,
    "completion_score": 0.85,
    "status_message": "Brief status description",
    "missing_requirements": ["list", "of", "missing", "items"],
    "completion_indicators": ["list", "of", "completed", "items"]
}}"""),
        ("user", """Task: {task}

Current State:
- Phone calls made: {phone_calls_made}
- Successful calls: {successful_calls}
- Research results: {research_results}
- Key facts documented: {key_facts_count}
- Latest call successful: {latest_call_success}
- Has research data: {has_research_data}

Analyze if this task is complete and provide your assessment.""")
    ])
    
    try:
        chain = prompt | mistral_llm
        response = chain.invoke(context)
        
        # Parse JSON response with robust extraction
        try:
            response_text = response.content.strip()
            
            # Try direct JSON parsing first
            try:
                result = json.loads(response_text)
            except json.JSONDecodeError:
                # If direct parsing fails, try to extract JSON from the response
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    result = json.loads(json_str)
                else:
                    raise Exception("No JSON found in response")
            
            return result
            
        except Exception as json_error:
            print(f"⚠️ Mistral JSON parsing failed: {json_error}")
            print(f"Raw response: {response.content[:500]}...")
            # Continue to fallback logic below
        
    except Exception as e:
        # Fallback to simple logic if Mistral fails
        completion_indicators = []
        missing_requirements = []
        
        # Check requirements based on task keywords
        needs_call = any(keyword in task.lower() for keyword in ["call", "phone", "contact"])
        needs_research = any(keyword in task.lower() for keyword in ["research", "find", "search", "information"])
        
        if needs_call:
            if context["successful_calls"] > 0:
                completion_indicators.append("Phone call executed successfully")
            else:
                missing_requirements.append("Successful phone call execution")
        
        if needs_research:
            if context["has_research_data"]:
                completion_indicators.append("Research information gathered")
            else:
                missing_requirements.append("Research data needs to be collected")
        
        if context["key_facts_count"] > 0:
            completion_indicators.append("Key facts documented")
        
        is_complete = len(missing_requirements) == 0 and len(completion_indicators) > 0
        completion_score = len(completion_indicators) / max(1, len(completion_indicators) + len(missing_requirements))
        
        status_message = ""
        if is_complete:
            status_message = f"Task completed. Achieved: {', '.join(completion_indicators)}"
        else:
            status_message = f"Task in progress. Missing: {', '.join(missing_requirements)}"
        
        return {
            "is_complete": is_complete,
            "completion_score": completion_score,
            "status_message": status_message,
            "missing_requirements": missing_requirements,
            "completion_indicators": completion_indicators
        }


def planner_node(state: AgentState):
    """
    Planning node that analyzes the current task and determines next steps using Mistral.
    """
    messages = state.get("messages", [])
    current_task = state.get("current_task", "")
    step_count = state.get("step_count", 0)
    
    # If no task is set, extract it from the last message
    if not current_task and messages:
        last_message = messages[-1]
        if isinstance(last_message, HumanMessage):
            current_task = last_message.content
    
    # Use Mistral for intelligent planning
    context = {
        "task": current_task,
        "step_count": step_count,
        "messages_count": len(messages),
        "phone_results": len(state.get("phone_call_results", [])),
        "research_results": len(state.get("tavily_results", [])),
        "key_facts": len(state.get("key_facts", {}))
    }
    
    planning_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an intelligent task planning agent. Analyze the current task and state to create a comprehensive plan.

Consider:
- What has been accomplished so far
- What still needs to be done
- Priority of remaining actions
- Resource requirements

Respond with a brief, actionable plan summary (2-3 sentences max)."""),
        ("user", """Task: {task}
Step: {step_count}
Phone calls made: {phone_results}
Research completed: {research_results}
Key facts gathered: {key_facts}

Provide your planning analysis.""")
    ])
    
    try:
        chain = planning_prompt | mistral_llm
        planning_response = chain.invoke(context)
        plan_message = f"Step {step_count + 1}: {planning_response.content}"
    except Exception as e:
        plan_message = f"Step {step_count + 1}: Analyzing task progress and determining next actions."
    
    # Check task completion
    completion_analysis = analyze_task_completion(state)
    
    new_messages = [AIMessage(content=plan_message)]
    
    if completion_analysis["is_complete"]:
        completion_message = f"Task analysis complete: {completion_analysis['status_message']}"
        new_messages.append(AIMessage(content=completion_message))
        return {
            "messages": new_messages,
            "current_task": current_task,
            "task_complete": True,
            "completion_status": completion_analysis["status_message"],
            "missing_requirements": [],
            "step_count": step_count + 1
        }
    else:
        return {
            "messages": new_messages,
            "current_task": current_task,
            "task_complete": False,
            "completion_status": completion_analysis["status_message"],
            "missing_requirements": completion_analysis["missing_requirements"],
            "step_count": step_count + 1
        }


def research_node(state: AgentState):
    """
    Research node that uses Mistral to generate intelligent search queries and analyze results.
    """
    current_task = state.get("current_task", "")
    missing_requirements = state.get("missing_requirements", [])
    existing_facts = state.get("key_facts", {})
    
    # Use Mistral to generate optimal search query
    query_context = {
        "task": current_task,
        "missing_requirements": ", ".join(missing_requirements),
        "existing_facts_count": len(existing_facts)
    }
    
    query_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert research query optimizer. Generate the most effective search query to gather information for the given task.

Consider:
- The main objective of the task
- What information is missing
- What would be most valuable to find

Respond with just the optimized search query (no explanations)."""),
        ("user", """Task: {task}
Missing requirements: {missing_requirements}
Existing facts: {existing_facts_count}

Generate the optimal search query.""")
    ])
    
    try:
        chain = query_prompt | mistral_llm
        query_response = chain.invoke(query_context)
        search_query = query_response.content.strip()
    except Exception as e:
        # Fallback to basic query generation
        search_query = current_task
        if "research" in " ".join(missing_requirements).lower():
            search_query = f"{current_task} information details"
    
    # Perform search
    search_result = search_tavily(search_query)
    
    # Update state
    tavily_results = state.get("tavily_results", [])
    tavily_results.append(search_result)
    
    # Use Mistral to analyze and extract key facts from search results
    key_facts = state.get("key_facts", {})
    if search_result.get("success") and search_result.get("results"):
        results_text = "\n".join([
            f"Title: {r.get('title', '')}\nContent: {r.get('content', '')[:300]}..."
            for r in search_result["results"][:3]
        ])
        
        analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert information analyst. Extract the most important key facts from search results relevant to the given task.

Extract 3-5 key facts in JSON format:
{
    "key_facts": [
        {
            "title": "Brief title",
            "content": "Key information (max 150 chars)",
            "relevance": "high/medium/low"
        }
    ]
}"""),
            ("user", """Task: {task}
Search Query: {search_query}

Search Results:
{results_text}

Extract the key facts most relevant to completing this task.""")
        ])
        
        try:
            analysis_context = {
                "task": current_task,
                "search_query": search_query,
                "results_text": results_text
            }
            chain = analysis_prompt | mistral_llm
            analysis_response = chain.invoke(analysis_context)
            
            # Parse extracted facts
            extracted_facts = json.loads(analysis_response.content)
            for i, fact in enumerate(extracted_facts.get("key_facts", [])):
                fact_key = f"research_{len(key_facts) + i + 1}"
                key_facts[fact_key] = {
                    "title": fact.get("title", ""),
                    "content": fact.get("content", ""),
                    "relevance": fact.get("relevance", "medium"),
                    "source": "mistral_analysis",
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            # Fallback to simple fact extraction
            for result in search_result["results"][:3]:
                fact_key = f"research_{len(key_facts) + 1}"
                key_facts[fact_key] = {
                    "title": result.get("title", ""),
                    "content": result.get("content", "")[:200] + "...",
                    "url": result.get("url", ""),
                    "relevance": "unknown",
                    "source": "direct_extract",
                    "timestamp": datetime.now().isoformat()
                }
    
    new_messages = [AIMessage(
        content=f"Research completed using query: '{search_query}'. Found {len(search_result.get('results', []))} results and extracted {len(key_facts) - len(existing_facts)} new key facts."
    )]
    
    return {
        "messages": new_messages,
        "tavily_results": tavily_results,
        "key_facts": key_facts
    }


def phone_call_node(state: AgentState):
    """
    Phone call node that uses Mistral to generate optimized call scripts and executes calls via ElevenLabs and Twilio.
    """
    current_task = state.get("current_task", "")
    key_facts = state.get("key_facts", {})
    phone_number = os.getenv("TARGET_PHONE_NUMBER", "+1234567890")
    
    # Use Mistral to generate an optimized call script
    call_context = {
        "task": current_task,
        "phone_number": phone_number,
        "key_facts_summary": "; ".join([
            f"{fact.get('title', '')}: {fact.get('content', '')[:50]}..."
            for fact in key_facts.values()
            if isinstance(fact, dict)
        ][:3])  # Top 3 key facts
    }
    
    script_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert phone call script writer. Create a concise, professional call script for the given task.

Guidelines:
- Be clear and direct
- Include relevant context from research
- Keep it conversational but professional
- Maximum 3-4 sentences
- Include specific call-to-action

Respond with just the call script (no explanations)."""),
        ("user", """Task: {task}
Phone Number: {phone_number}
Research Context: {key_facts_summary}

Generate the optimized call script.""")
    ])
    
    try:
        chain = script_prompt | mistral_llm
        script_response = chain.invoke(call_context)
        enhanced_task = script_response.content.strip()
    except Exception as e:
        # Fallback to original task if Mistral fails
        enhanced_task = current_task
        if key_facts:
            # Add some context from key facts
            context_snippet = next(iter(key_facts.values())).get("content", "")[:100] if key_facts else ""
            if context_snippet:
                enhanced_task += f" Context: {context_snippet}"
    
    # Make the call with enhanced script using ElevenLabs API
    call_result = call_elevenlabs_outbound(enhanced_task, phone_number)
    
    # Update state
    phone_call_results = state.get("phone_call_results", [])
    phone_call_results.append(call_result)
    
    # Add to key facts with enhanced information
    key_facts[f"phone_call_{len(phone_call_results)}"] = {
        "original_task": current_task,
        "enhanced_script": enhanced_task,
        "phone_number": phone_number,
        "success": call_result.get("success", False),
        "call_id": call_result.get("call_id", ""),
        "timestamp": call_result.get("timestamp", ""),
        "call_priority": call_result.get("call_priority", "normal")
    }
    
    status = "successful" if call_result.get("success") else "failed"
    call_id = call_result.get("call_id", "N/A")
    
    new_messages = [AIMessage(
        content=f"Phone call {status} to {phone_number}. Call ID: {call_id}. Used enhanced script generated by Mistral."
    )]
    
    return {
        "messages": new_messages,
        "phone_call_results": phone_call_results,
        "key_facts": key_facts
    }


def should_continue(state: AgentState) -> str:
    """
    Determines the next step based on current state using Mistral for intelligent routing.
    """
    if state.get("task_complete", False):
        return END
    
    missing_requirements = state.get("missing_requirements", [])
    step_count = state.get("step_count", 0)
    current_task = state.get("current_task", "")
    
    # Prevent infinite loops
    if step_count > 10:
        return END
    
    # Use Mistral for intelligent routing decision
    routing_context = {
        "task": current_task,
        "step_count": step_count,
        "missing_requirements": ", ".join(missing_requirements),
        "phone_calls_made": len(state.get("phone_call_results", [])),
        "research_completed": len(state.get("tavily_results", [])),
        "key_facts_count": len(state.get("key_facts", {}))
    }
    
    routing_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an intelligent workflow router. Decide the next best action based on the current state.

Available actions:
- "research": Gather information via web search
- "phone_call": Make a phone call  
- "planner": Re-analyze and plan next steps

Choose the most logical next step. Respond with ONLY the action name (research/phone_call/planner)."""),
        ("user", """Task: {task}
Step: {step_count}
Missing: {missing_requirements}
Phone calls made: {phone_calls_made}
Research done: {research_completed}
Key facts: {key_facts_count}

What should be the next action?""")
    ])
    
    try:
        chain = routing_prompt | mistral_llm
        routing_response = chain.invoke(routing_context)
        next_action = routing_response.content.strip().lower()
        
        # Validate the response
        valid_actions = ["research", "phone_call", "planner"]
        if next_action in valid_actions:
            return next_action
        else:
            # Fallback to rule-based routing
            return _fallback_routing(missing_requirements)
            
    except Exception as e:
        # Fallback to rule-based routing if Mistral fails
        return _fallback_routing(missing_requirements)

def _fallback_routing(missing_requirements: List[str]) -> str:
    """Fallback routing logic when Mistral is unavailable."""
    if any("phone call" in req.lower() for req in missing_requirements):
        return "phone_call"
    elif any("research" in req.lower() or "information" in req.lower() for req in missing_requirements):
        return "research"
    else:
        return "planner"


# Create the graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("planner", planner_node)
workflow.add_node("research", research_node)
workflow.add_node("phone_call", phone_call_node)

# Add edges
workflow.add_edge("research", "planner")
workflow.add_edge("phone_call", "planner")

# Add conditional edges
workflow.add_conditional_edges(
    "planner",
    should_continue,
    {
        "research": "research",
        "phone_call": "phone_call",
        END: END
    }
)

# Set entry point
workflow.set_entry_point("planner")

# Compile the graph
app = workflow.compile()


def run_agent(task: str, phone_number: str = None) -> Dict[str, Any]:
    """
    Run the agent with a specific task.
    
    Args:
        task: The task to execute
        phone_number: Optional phone number to call
        
    Returns:
        Final state of the agent
    """
    if phone_number:
        os.environ["TARGET_PHONE_NUMBER"] = phone_number
    
    initial_state = {
        "messages": [HumanMessage(content=task)],
        "current_task": task,
        "task_complete": False,
        "completion_status": "",
        "missing_requirements": [],
        "key_facts": {},
        "tavily_results": [],
        "phone_call_results": [],
        "step_count": 0
    }
    
    # Run the workflow
    final_state = app.invoke(initial_state)
    
    return final_state


if __name__ == "__main__":
    # Example usage
    task = "Call the client and confirm their meeting schedule for next week"
    phone_number = "+1234567890"  # Replace with actual phone number
    
    result = run_agent(task, phone_number)
    
    print("Agent execution completed!")
    print(f"Task: {result['current_task']}")
    print(f"Completed: {result['task_complete']}")
    print(f"Status: {result['completion_status']}")
    print(f"Key Facts: {json.dumps(result['key_facts'], indent=2)}") 