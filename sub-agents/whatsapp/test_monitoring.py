#!/usr/bin/env python3
"""
Test script for WhatsApp monitoring functionality
"""
import requests
import time
import json

BASE_URL = "http://localhost:8000"

def test_monitoring():
    """Test the monitoring functionality"""
    
    print("=== WhatsApp Message Monitoring Test ===\n")
    
    # 1. Check health
    print("1. Checking server health...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"   Status: {response.json()}")
    
    # 2. Get current monitoring status
    print("\n2. Checking monitoring status...")
    response = requests.get(f"{BASE_URL}/monitoring_status")
    status = response.json()
    print(f"   Current status: {json.dumps(status, indent=2)}")
    
    # 3. Start monitoring with custom config
    print("\n3. Starting monitoring with custom configuration...")
    config = {
        "check_interval_minutes": 1,  # Check every minute
        "auto_respond": True,
        "response_context": "You are Prosusware, a helpful travel and food ordering assistant. Respond naturally and helpfully.",
        "ignore_own_messages": True,
        "only_respond_to_direct_messages": True
    }
    
    response = requests.post(f"{BASE_URL}/start_monitoring", json=config)
    result = response.json()
    print(f"   Start result: {json.dumps(result, indent=2)}")
    
    # 4. Monitor for a few minutes
    print("\n4. Monitoring for new messages (will check status every 30 seconds)...")
    print("   Send some WhatsApp messages to test the auto-response feature!")
    
    for i in range(6):  # Monitor for 3 minutes
        time.sleep(30)
        
        # Get status
        response = requests.get(f"{BASE_URL}/monitoring_status")
        status = response.json()
        print(f"   [{i+1}/6] Status: Enabled={status['enabled']}, Processed={status['processed_messages_count']}")
        
        # Get recent logs
        response = requests.get(f"{BASE_URL}/monitoring_logs?limit=5")
        logs = response.json()
        if logs['logs']:
            print("   Recent logs:")
            for log in logs['logs'][-3:]:  # Show last 3 logs
                print(f"     [{log['type']}] {log['message']}")
    
    # 5. Stop monitoring
    print("\n5. Stopping monitoring...")
    response = requests.post(f"{BASE_URL}/stop_monitoring")
    result = response.json()
    print(f"   Stop result: {result}")
    
    # 6. Get final logs
    print("\n6. Getting final monitoring logs...")
    response = requests.get(f"{BASE_URL}/monitoring_logs")
    logs = response.json()
    print(f"   Total logs: {logs['total_logs']}")
    
    if logs['logs']:
        print("   Recent activity:")
        for log in logs['logs'][-10:]:  # Show last 10 logs
            timestamp = log['timestamp'].split('T')[1][:8]  # Just time part
            print(f"     [{timestamp}] [{log['type']}] {log['message']}")
    
    print("\n=== Test completed ===")

def test_manual_task():
    """Test sending a manual task"""
    print("\n=== Manual Task Test ===")
    
    task_request = {
        "task": "Check for any new messages in the last 5 minutes and respond to them appropriately",
        "max_iterations": 5
    }
    
    print("Sending manual task...")
    response = requests.post(f"{BASE_URL}/execute_task", json=task_request)
    result = response.json()
    
    print(f"Task result: {result['status']}")
    print(f"Message: {result['message']}")
    
    if result['execution_log']:
        print("Execution log:")
        for log_entry in result['execution_log'][-5:]:  # Show last 5 entries
            print(f"  [{log_entry['type']}] {log_entry['message'][:100]}...")

if __name__ == "__main__":
    try:
        test_monitoring()
        
        # Optionally test manual task
        user_input = input("\nWould you like to test a manual task? (y/n): ")
        if user_input.lower() == 'y':
            test_manual_task()
            
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to the server. Make sure it's running on localhost:8000")
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"ERROR: {e}") 