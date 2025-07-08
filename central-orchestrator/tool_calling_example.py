#!/usr/bin/env python3
"""
Example usage of the Tool Calling Agent

This demonstrates how to use the refactored agent that uses tool calling
instead of the node-based LangGraph approach.
"""

import os
from tool_calling_agent import run_tool_calling_agent, ToolCallingAgent


def example_pizza_order():
    """Example: Ordering pizza using the tool calling agent"""
    print("="*80)
    print("EXAMPLE 1: Pizza Order")
    print("="*80)
    
    task = "Book me a flight."
    user_id = "686a6dda9030f92d7aeaaeb0"
    conversation_id = "686a80819030f92d7aeaaeb2"  # Optional conversation tracking ID
    
    result = run_tool_calling_agent(
        task=task,
        user_id=user_id,
        conversation_id=conversation_id,
        max_iterations=8
    )
    
    print_results(result)
    return result


def example_phone_call_with_known_number():
    """Example: Making a call when you already have the phone number"""
    print("="*80)
    print("EXAMPLE 2: Call with Known Number")
    print("="*80)
    
    # Initialize the agent
    agent = ToolCallingAgent(user_id="user_call_001", max_iterations=5)
    
    task = "Call mum and let her know I'm coming to see her. Her phone number is +447449313570"
    conversation_id = "family_call_001"
    
    result = agent.run(task, conversation_id=conversation_id)
    
    print_results(result)
    return result


def example_information_gathering():
    """Example: Pure information gathering without phone calls"""
    print("="*80)
    print("EXAMPLE 3: Information Gathering")
    print("="*80)
    
    task = "Find information about the best Italian restaurants in London with their contact details"
    
    result = run_tool_calling_agent(
        task=task,
        user_id="user_info_001",
        max_iterations=6
    )
    
    print_results(result)
    return result


def example_with_sleep():
    """Example: Task that might need waiting/sleeping"""
    print("="*80)
    print("EXAMPLE 4: Task with Sleep")
    print("="*80)
    
    task = "Call a restaurant to make a reservation, wait a minute, then call back to confirm"
    
    result = run_tool_calling_agent(
        task=task,
        user_id="user_sleep_001",
        max_iterations=10
    )
    
    print_results(result)
    return result


def example_direct_tool_usage():
    """Example: Using individual tools directly"""
    print("="*80)
    print("EXAMPLE 5: Direct Tool Usage")
    print("="*80)
    
    from tool_calling_agent import web_search, make_outbound_call, sleep_tool
    
    # Search for information
    print("🔍 Direct web search...")
    search_result = web_search.invoke({
        "query": "best pizza delivery London phone number",
        "max_results": 5
    })
    print(f"Search found {search_result['result_count']} results")
    
    # Sleep for a moment
    print("\n😴 Direct sleep...")
    sleep_result = sleep_tool.invoke({"duration_seconds": 3})
    print(f"Sleep result: {sleep_result['message']}")
    
    # Make a phone call (if phone number found)
    if search_result.get('phone_numbers_found'):
        phone_number = search_result['phone_numbers_found'][0]['number']
        print(f"\n📞 Direct phone call to {phone_number}...")
        
        call_result = make_outbound_call.invoke({
            "task": "Order a large pepperoni pizza for delivery",
            "phone_number": phone_number
        })
        print(f"Call result: {call_result.get('success', False)}")
    
    return {
        "search_result": search_result,
        "sleep_result": sleep_result,
        "call_result": call_result if search_result.get('phone_numbers_found') else None
    }


def example_global_tools_usage():
    """Example: Using the new global tools"""
    print("="*80)
    print("EXAMPLE 6: Global Tools Usage")
    print("="*80)
    
    agent = ToolCallingAgent(user_id="686a6dda9030f92d7aeaaeb0", max_iterations=12)
    
    task = """
    First, add a new contact for my colleague, Sarah Connor. Her email is 'sarah.c@skynet.com' and phone is '555-0102'.
    Next, add a memory for Sarah: 'She is a key stakeholder in the T-800 project'.
    Then, search my memories for anything related to the 'T-800 project'.
    Finally, write a status update that the initial setup for Sarah Connor is complete. My conversation ID is 'conv-global-tools-test'.
    """
    
    result = agent.run(task, conversation_id="conv-global-tools-test")
    print_results(result)
    return result


def example_serp_search():
    """Example: Using the new SERP search tool"""
    print("="*80)
    print("EXAMPLE 7: SERP Search (Flights)")
    print("="*80)
    
    agent = ToolCallingAgent(user_id="user_serp_001", max_iterations=5)
    
    task = "Find a round trip flight from London (LHR) to Rome (FCO) for next week."
    
    result = agent.run(task, conversation_id="serp_flights_test_001")
    print_results(result)
    return result


def example_whatsapp_task():
    """Example: Using the WhatsApp agent to execute a task"""
    print("="*80)
    print("EXAMPLE 8: WhatsApp Task")
    print("="*80)
    
    agent = ToolCallingAgent(user_id="686be51b386780da3a6bbdb5", max_iterations=5)
    
    task = "Use the WhatsApp agent to ask Alex Choi on +447777777777 when they are available to go to Paris this summer"
    conversation_id = "whatsapp_paris_trip_001"
    
    result = agent.run(task, conversation_id=conversation_id)
    print_results(result)
    return result


def print_results(result):
    """Helper function to print agent results in a nice format"""
    print("\n" + "="*60)
    print("EXECUTION RESULTS")
    print("="*60)
    
    print(f"Task: {result['task']}")
    print(f"User ID: {result.get('user_id', 'None')}")
    print(f"Conversation ID: {result.get('conversation_id', 'None')}")
    print(f"Iterations: {result['iterations']}")
    print(f"Timestamp: {result['timestamp']}")
    
    context = result['context']
    print(f"\nSearch Results: {len(context['search_results'])}")
    print(f"Phone Calls Made: {len(context['phone_calls'])}")
    print(f"Phone Numbers Found: {len(context['found_phone_numbers'])}")
    
    print(f"\nInitial Plan:")
    for i, step in enumerate(context['plan'], 1):
        print(f"  {i}. {step}")
    
    print(f"\nFinal Response:")
    print(f"  {result['final_response']}")
    
    # Show execution log
    if result.get('execution_log'):
        print(f"\nExecution Log:")
        for log_entry in result['execution_log']:
            tool_name = log_entry.get('tool', log_entry.get('action'))
            iteration = log_entry.get('iteration', log_entry.get('step'))
            success = log_entry['result'].get('success', 'unknown')
            print(f"  Iteration {iteration}: {tool_name} -> {success}")
    
    print("="*60)


def main():
    """Run all examples"""
    print("🚀 Tool Calling Agent Examples")
    print("These examples demonstrate the refactored agent architecture")
    print("Make sure you have set the required environment variables:")
    print("- GOOGLE_API_KEY")
    print("- TAVILY_API_KEY") 
    print("- ELEVENLABS_API_KEY")
    print("- ELEVENLABS_AGENT_ID")
    print("- ELEVENLABS_PHONE_NUMBER_ID")
    print()
    
    # Check environment variables
    required_vars = [
        "GOOGLE_API_KEY", "TAVILY_API_KEY", "ELEVENLABS_API_KEY",
        "ELEVENLABS_AGENT_ID", "ELEVENLABS_PHONE_NUMBER_ID"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(f"⚠️ Missing environment variables: {', '.join(missing_vars)}")
        print("Some examples may not work properly.")
        print()
    
    try:
        # Run examples
        print("Running examples...")
        
        # Example 1: Pizza order (requires search + phone call)
        example_pizza_order()
        
        # Example 2: Direct call with known number
        #example_phone_call_with_known_number()
        
        # Example 3: Information gathering only
        #example_information_gathering()
        
        # Example 4: Task with sleep
        #example_with_sleep()
        
        # Example 5: Direct tool usage
        #example_direct_tool_usage()
        
        # Example 6: Global tools
        #example_global_tools_usage()
        
        # Example 7: SERP Search
        #example_serp_search()
        
        # Example 8: WhatsApp Task
        #example_whatsapp_task()
        
        print("\n🎉 All examples completed!")
        
    except KeyboardInterrupt:
        print("\n⏹️ Examples interrupted by user")
    except Exception as e:
        print(f"\n❌ Error running examples: {str(e)}")


if __name__ == "__main__":
    main() 