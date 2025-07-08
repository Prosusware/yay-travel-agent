#!/usr/bin/env python3
"""
Test script to verify the LangGraph agent setup and dependencies.
"""

import os
import sys
from typing import Dict, Any

def test_imports() -> Dict[str, Any]:
    """Test if all required packages can be imported."""
    results = {"imports": {}}
    
    try:
        import langgraph
        results["imports"]["langgraph"] = {"status": "✓", "version": getattr(langgraph, "__version__", "unknown")}
    except ImportError as e:
        results["imports"]["langgraph"] = {"status": "✗", "error": str(e)}
    
    try:
        import langchain_core
        results["imports"]["langchain_core"] = {"status": "✓", "version": getattr(langchain_core, "__version__", "unknown")}
    except ImportError as e:
        results["imports"]["langchain_core"] = {"status": "✗", "error": str(e)}
    
    try:
        import langchain_mistralai
        results["imports"]["langchain_mistralai"] = {"status": "✓", "version": getattr(langchain_mistralai, "__version__", "unknown")}
    except ImportError as e:
        results["imports"]["langchain_mistralai"] = {"status": "✗", "error": str(e)}
    
    try:
        import tavily
        results["imports"]["tavily"] = {"status": "✓", "version": getattr(tavily, "__version__", "unknown")}
    except ImportError as e:
        results["imports"]["tavily"] = {"status": "✗", "error": str(e)}
    
    try:
        import requests
        results["imports"]["requests"] = {"status": "✓", "version": requests.__version__}
    except ImportError as e:
        results["imports"]["requests"] = {"status": "✗", "error": str(e)}
    
    return results

def test_environment_variables() -> Dict[str, Any]:
    """Test if required environment variables are set."""
    required_vars = [
        "MISTRAL_API_KEY",
        "TAVILY_API_KEY",
        "ELEVENLABS_API_KEY",
        "ELEVENLABS_AGENT_ID",
        "ELEVENLABS_PHONE_NUMBER_ID",
        "TARGET_PHONE_NUMBER"
    ]
    
    results = {"env_vars": {}}
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if "key" in var.lower() or "token" in var.lower():
                masked_value = value[:4] + "*" * (len(value) - 8) + value[-4:] if len(value) > 8 else "*" * len(value)
                results["env_vars"][var] = {"status": "✓", "value": masked_value}
            else:
                results["env_vars"][var] = {"status": "✓", "value": value}
        else:
            results["env_vars"][var] = {"status": "✗", "value": "Not set"}
    
    return results

def test_agent_imports() -> Dict[str, Any]:
    """Test if the agent modules can be imported."""
    results = {"agent_imports": {}}
    
    try:
        from agent import run_agent, AgentState
        results["agent_imports"]["basic_agent"] = {"status": "✓", "functions": ["run_agent", "AgentState"]}
    except ImportError as e:
        results["agent_imports"]["basic_agent"] = {"status": "✗", "error": str(e)}
    
    try:
        from advanced_agent import run_enhanced_agent, AdvancedAgentState
        results["agent_imports"]["advanced_agent"] = {"status": "✓", "functions": ["run_enhanced_agent", "AdvancedAgentState"]}
    except ImportError as e:
        results["agent_imports"]["advanced_agent"] = {"status": "✗", "error": str(e)}
    
    return results

def test_mistral_connection() -> Dict[str, Any]:
    """Test connection to Mistral API."""
    results = {"mistral_connection": {}}
    
    try:
        from langchain_mistralai import ChatMistralAI
        api_key = os.getenv("MISTRAL_API_KEY")
        
        if not api_key:
            results["mistral_connection"]["status"] = "✗"
            results["mistral_connection"]["error"] = "No API key provided"
            return results
        
        llm = ChatMistralAI(
            api_key=api_key,
            model=os.getenv("MISTRAL_MODEL", "mistral-large-latest"),
            temperature=0.1
        )
        
        # Try a simple completion
        response = llm.invoke("Hello, this is a test. Respond with 'OK'.")
        
        if response and hasattr(response, 'content'):
            results["mistral_connection"]["status"] = "✓"
            results["mistral_connection"]["message"] = "Connection successful"
        else:
            results["mistral_connection"]["status"] = "?"
            results["mistral_connection"]["message"] = "Unusual response format"
    
    except Exception as e:
        results["mistral_connection"]["status"] = "✗"
        results["mistral_connection"]["error"] = str(e)
    
    return results

def test_tavily_connection() -> Dict[str, Any]:
    """Test connection to Tavily API."""
    results = {"tavily_connection": {}}
    
    try:
        from tavily import TavilyClient
        api_key = os.getenv("TAVILY_API_KEY")
        
        if not api_key:
            results["tavily_connection"]["status"] = "✗"
            results["tavily_connection"]["error"] = "No API key provided"
            return results
        
        client = TavilyClient(api_key=api_key)
        
        # Try a simple search
        response = client.search(query="test", max_results=1)
        
        if response and "results" in response:
            results["tavily_connection"]["status"] = "✓"
            results["tavily_connection"]["message"] = "Connection successful"
        else:
            results["tavily_connection"]["status"] = "?"
            results["tavily_connection"]["message"] = "Unusual response format"
    
    except Exception as e:
        results["tavily_connection"]["status"] = "✗"
        results["tavily_connection"]["error"] = str(e)
    
    return results

def print_results(results: Dict[str, Any]):
    """Print test results in a formatted way."""
    print("="*60)
    print("LANGRAPH AGENT SETUP TEST RESULTS")
    print("="*60)
    
    # Package imports
    print("\n📦 PACKAGE IMPORTS:")
    for package, info in results.get("imports", {}).items():
        status = info["status"]
        if status == "✓":
            version = info.get("version", "unknown")
            print(f"  {status} {package} (v{version})")
        else:
            print(f"  {status} {package} - ERROR: {info.get('error', 'Unknown error')}")
    
    # Environment variables
    print("\n🔧 ENVIRONMENT VARIABLES:")
    for var, info in results.get("env_vars", {}).items():
        status = info["status"]
        value = info["value"]
        print(f"  {status} {var}: {value}")
    
    # Agent imports
    print("\n🤖 AGENT MODULES:")
    for agent, info in results.get("agent_imports", {}).items():
        status = info["status"]
        if status == "✓":
            functions = ", ".join(info.get("functions", []))
            print(f"  {status} {agent} ({functions})")
        else:
            print(f"  {status} {agent} - ERROR: {info.get('error', 'Unknown error')}")
    
    # API connections
    print("\n🌐 API CONNECTIONS:")
    
    # Mistral API
    mistral_status = results.get("mistral_connection", {}).get("status", "✗")
    if mistral_status == "✓":
        message = results["mistral_connection"].get("message", "OK")
        print(f"  {mistral_status} Mistral API: {message}")
    else:
        error = results.get("mistral_connection", {}).get("error", "Unknown error")
        print(f"  {mistral_status} Mistral API: {error}")
    
    # Tavily API
    tavily_status = results.get("tavily_connection", {}).get("status", "✗")
    if tavily_status == "✓":
        message = results["tavily_connection"].get("message", "OK")
        print(f"  {tavily_status} Tavily API: {message}")
    else:
        error = results.get("tavily_connection", {}).get("error", "Unknown error")
        print(f"  {tavily_status} Tavily API: {error}")
    
    # Summary
    print("\n" + "="*60)
    
    # Count issues
    issues = []
    for category in results.values():
        if isinstance(category, dict):
            for item, info in category.items():
                if isinstance(info, dict) and info.get("status") == "✗":
                    issues.append(f"{item}")
    
    if not issues:
        print("🎉 ALL TESTS PASSED! Your setup is ready to go.")
        print("\nNext steps:")
        print("1. Run 'python example_usage.py' to see the agents in action")
        print("2. Or run 'python agent.py' for the basic agent")
        print("3. Or run 'python advanced_agent.py' for the advanced agent")
    else:
        print(f"⚠️  {len(issues)} ISSUES FOUND:")
        for issue in issues:
            print(f"   - {issue}")
        print("\nPlease fix these issues before running the agents.")
        
        if any("env_vars" in str(issue) for issue in issues):
            print("\n💡 Environment variable issues can be fixed by:")
            print("   1. Copying 'config.env.example' to '.env'")
            print("   2. Filling in your API keys and configuration")
        
        if any("import" in str(issue) for issue in issues):
            print("\n💡 Import issues can be fixed by:")
            print("   1. Running 'pip install -r requirements.txt'")
            print("   2. Making sure you're in the correct virtual environment")

def main():
    """Run all tests and print results."""
    print("Testing LangGraph Agent Setup...")
    print("This may take a moment to test API connections...\n")
    
    # Collect all test results
    all_results = {}
    all_results.update(test_imports())
    all_results.update(test_environment_variables())
    all_results.update(test_agent_imports())
    all_results.update(test_mistral_connection())
    all_results.update(test_tavily_connection())
    
    # Print formatted results
    print_results(all_results)

if __name__ == "__main__":
    main() 