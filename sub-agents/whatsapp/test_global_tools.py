#!/usr/bin/env python3
"""
Test script for global tools integration with WhatsApp agent
"""

import os
import asyncio
from main import WhatsAppAgent
from global_tools import get_global_tools

def test_global_tools_import():
    """Test that global tools can be imported and retrieved"""
    try:
        tools = get_global_tools()
        print(f"✅ Successfully imported {len(tools)} global tools:")
        for tool in tools:
            print(f"   - {tool.name}: {tool.description}")
        return True
    except Exception as e:
        print(f"❌ Failed to import global tools: {e}")
        return False

def test_agent_initialization():
    """Test that the WhatsApp agent can be initialized with global tools"""
    try:
        agent = WhatsAppAgent()
        total_tools = len(agent.tools)
        whatsapp_tools = len(agent.whatsapp_tools)
        global_tools = len(agent.global_tools)
        
        print(f"✅ Agent initialized successfully:")
        print(f"   - WhatsApp tools: {whatsapp_tools}")
        print(f"   - Global tools: {global_tools}")
        print(f"   - Total tools: {total_tools}")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
        return False

def test_tool_names():
    """Test that expected global tool names are present"""
    expected_tools = [
        'web_search',
        'add_contact_tool',
        'update_contact_tool',
        'get_contacts_tool',
        'add_memory_tool',
        'search_memory_tool',
        'write_status_tool',
        'read_status_tool',
        'store_documents_tool',
        'search_documents_tool'
    ]
    
    try:
        tools = get_global_tools()
        tool_names = [tool.name for tool in tools]
        
        missing_tools = []
        for expected_tool in expected_tools:
            if expected_tool not in tool_names:
                missing_tools.append(expected_tool)
        
        if missing_tools:
            print(f"❌ Missing expected tools: {missing_tools}")
            return False
        else:
            print("✅ All expected global tools are present")
            return True
    except Exception as e:
        print(f"❌ Failed to check tool names: {e}")
        return False

async def test_agent_execution():
    """Test that the agent can execute a simple task"""
    try:
        agent = WhatsAppAgent()
        
        # Simple test task
        result = await agent.execute_task(
            task="Test the global tools integration by checking available tools",
            max_iterations=2
        )
        
        if result.get("error"):
            print(f"❌ Agent execution failed: {result['error']}")
            return False
        else:
            print("✅ Agent execution completed successfully")
            print(f"   - Task completed: {result.get('task_completed', False)}")
            print(f"   - Iterations: {result.get('iterations', 0)}")
            return True
    except Exception as e:
        print(f"❌ Failed to execute agent task: {e}")
        return False

def main():
    """Run all tests"""
    print("🔧 Testing Global Tools Integration\n")
    
    tests = [
        ("Import Global Tools", test_global_tools_import),
        ("Agent Initialization", test_agent_initialization),
        ("Tool Names Check", test_tool_names),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        result = test_func()
        results.append(result)
    
    # Only run agent execution test if previous tests passed
    if all(results):
        print(f"\n📋 Running: Agent Execution Test")
        try:
            agent_result = asyncio.run(test_agent_execution())
            results.append(agent_result)
        except Exception as e:
            print(f"❌ Agent execution test failed: {e}")
            results.append(False)
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print(f"\n🎯 Test Summary:")
    print(f"   Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All tests passed! Global tools integration is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 