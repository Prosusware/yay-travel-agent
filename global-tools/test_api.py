#!/usr/bin/env python3
"""
Comprehensive test script for Global Tools API
Tests all endpoints and provides detailed status reporting
"""

import requests
import json
import time
import uuid
from typing import Dict, Any, Optional

class APITester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_results = []
        self.test_data = {
            "user_id": str(uuid.uuid4()),
            "contact_id": None,
            "conversation_id": str(uuid.uuid4()),
            "collection_name": f"test_collection_{int(time.time())}",
            "memory_id": None,
            "status_update_id": None
        }
        
    def log_test(self, endpoint: str, method: str, success: bool, details: str, response_time: float = 0):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            "endpoint": endpoint,
            "method": method,
            "status": status,
            "details": details,
            "response_time": round(response_time, 3)
        })
        print(f"{status} {method} {endpoint} - {details} ({response_time:.3f}s)")

    def test_endpoint(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                     params: Optional[Dict] = None, expected_status: int = 200) -> Optional[Dict]:
        """Generic endpoint tester"""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        try:
            if method == "GET":
                response = requests.get(url, params=params, timeout=10)
            elif method == "POST":
                response = requests.post(url, json=data, timeout=10)
            elif method == "PATCH":
                response = requests.patch(url, json=data, timeout=10)
            elif method == "DELETE":
                response = requests.delete(url, timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response_time = time.time() - start_time
            
            if response.status_code == expected_status:
                try:
                    response_data = response.json()
                    self.log_test(endpoint, method, True, f"Status {response.status_code}", response_time)
                    return response_data
                except json.JSONDecodeError:
                    self.log_test(endpoint, method, True, f"Status {response.status_code} (non-JSON)", response_time)
                    return {"raw_response": response.text}
            else:
                try:
                    error_data = response.json()
                    error_msg = error_data.get("message", "Unknown error")
                except:
                    error_msg = response.text[:100]
                self.log_test(endpoint, method, False, f"Status {response.status_code}: {error_msg}", response_time)
                return None
                
        except requests.exceptions.RequestException as e:
            response_time = time.time() - start_time
            self.log_test(endpoint, method, False, f"Request failed: {str(e)}", response_time)
            return None

    def run_basic_tests(self):
        """Test basic endpoints that should always work"""
        print("\n🔧 Testing Basic Endpoints...")
        
        # Test root endpoint
        self.test_endpoint("GET", "/")
        
        # Test health check
        health_data = self.test_endpoint("GET", "/health")
        
        # Test service info
        self.test_endpoint("GET", "/api/info")

    def run_database_tests(self):
        """Test database-dependent endpoints"""
        print("\n💾 Testing Database Endpoints...")
        
        # Test database status
        db_status = self.test_endpoint("GET", "/api/database/status")
        
        if not db_status:
            print("⚠️  Database not available - skipping database-dependent tests")
            return False
        
        # Create a test user first (since services require users to exist)
        self._create_test_user()
        
        # Test contact management
        print("\n👥 Testing Contact Management...")
        
        # Add a contact
        contact_data = {
            "UserID": self.test_data["user_id"],
            "contact": {
                "FirstName": "Test",
                "LastName": "User",
                "email": "test@example.com",
                "phoneNumber": "+1234567890",
                "nickname": "Tester"
            }
        }
        
        add_contact_response = self.test_endpoint("POST", "/api/contacts/add", contact_data)
        if add_contact_response:
            # Extract contact_id from the response structure
            contact = add_contact_response.get("contact", {})
            self.test_data["contact_id"] = contact.get("uid")
        
        # Get user contacts
        self.test_endpoint("GET", f"/api/contacts/{self.test_data['user_id']}")
        
        # Update contact
        if self.test_data["contact_id"]:
            update_data = {
                "UserID": self.test_data["user_id"],
                "contact_uid": self.test_data["contact_id"],
                "contact": {
                    "nickname": "Updated Tester"
                }
            }
            self.test_endpoint("PATCH", "/api/contacts/update", update_data)
        
        return True

    def run_search_tests(self):
        """Test search functionality"""
        print("\n🔍 Testing Search Functionality...")
        
        # Test web search (may fail if Tavily API not configured)
        search_params = {"query": "artificial intelligence"}
        self.test_endpoint("GET", "/api/search", params=search_params)

    def run_memory_tests(self):
        """Test memory management"""
        print("\n🧠 Testing Memory Management...")
        
        # Test adding user memory
        user_memory_data = {
            "user_id": self.test_data["user_id"],
            "memory": "This is a test memory for the user about artificial intelligence and machine learning."
        }
        
        memory_response = self.test_endpoint("POST", "/api/memory/add", user_memory_data)
        if memory_response:
            self.test_data["memory_id"] = memory_response.get("memory_id")
        
        # Test adding contact memory (if contact exists)
        if self.test_data["contact_id"]:
            contact_memory_data = {
                "user_id": self.test_data["user_id"],
                "contact_id": self.test_data["contact_id"],
                "memory": "This contact mentioned they are working on a new AI project."
            }
            self.test_endpoint("POST", "/api/memory/add", contact_memory_data)
        
        # Test memory search
        search_data = {
            "user_id": self.test_data["user_id"],
            "query": "artificial intelligence",
            "n_results": 5
        }
        self.test_endpoint("POST", "/api/memory/search", search_data)
        
        # Test memory search across all collections
        search_all_data = {
            "user_id": self.test_data["user_id"],
            "query": "AI project",
            "n_results": 5,
            "search_all_collections": True
        }
        self.test_endpoint("POST", "/api/memory/search", search_all_data)

    def run_vector_database_tests(self):
        """Test ChromaDB vector database functionality"""
        print("\n🔢 Testing Vector Database...")
        
        # Test vector database status
        vector_status = self.test_endpoint("GET", "/api/vector/status")
        
        if not vector_status or not vector_status.get("status") == "connected":
            print("⚠️  ChromaDB not available - skipping vector database tests")
            return
        
        # Test list collections
        self.test_endpoint("GET", "/api/vector/collections")
        
        # Test add documents to collection
        add_docs_data = {
            "collection_name": self.test_data["collection_name"],
            "documents": [
                "This is the first test document about machine learning.",
                "This is the second test document about artificial intelligence.",
                "This document discusses natural language processing."
            ],
            "metadatas": [
                {"topic": "ML", "type": "test"},
                {"topic": "AI", "type": "test"},
                {"topic": "NLP", "type": "test"}
            ],
            "ids": ["doc1", "doc2", "doc3"]
        }
        self.test_endpoint("POST", "/api/vector/documents/add", add_docs_data)
        
        # Test get collection info
        self.test_endpoint("GET", f"/api/vector/collections/{self.test_data['collection_name']}")
        
        # Test query documents
        query_data = {
            "collection_name": self.test_data["collection_name"],
            "query_texts": ["machine learning algorithms"],
            "n_results": 2
        }
        self.test_endpoint("POST", "/api/vector/documents/query", query_data)
        
        # Test update documents
        update_docs_data = {
            "collection_name": self.test_data["collection_name"],
            "ids": ["doc1"],
            "metadatas": [{"topic": "ML", "type": "test", "updated": True}]
        }
        self.test_endpoint("PATCH", "/api/vector/documents/update", update_docs_data)
        
        # Test delete documents
        delete_docs_data = {
            "collection_name": self.test_data["collection_name"],
            "ids": ["doc3"]
        }
        self.test_endpoint("POST", "/api/vector/documents/delete", delete_docs_data)
        
        # Clean up - delete test collection
        self.test_endpoint("DELETE", f"/api/vector/collections/{self.test_data['collection_name']}")

    def run_status_update_tests(self):
        """Test status update functionality"""
        print("\n📝 Testing Status Update Management...")
        
        # Test writing status updates
        status_data = {
            "agent_id": "test-agent-001",
            "agent_type": "assistant",
            "conversation_id": self.test_data["conversation_id"],
            "update": "This is a test status update from the testing agent."
        }
        
        status_response = self.test_endpoint("POST", "/api/status/write", status_data)
        if status_response:
            self.test_data["status_update_id"] = status_response.get("status_update_id")
        
        # Write another status update with different agent
        status_data2 = {
            "agent_id": "test-agent-002",
            "agent_type": "researcher",
            "conversation_id": self.test_data["conversation_id"],
            "update": "This is another test status update from a different agent type."
        }
        self.test_endpoint("POST", "/api/status/write", status_data2)
        
        # Test reading all status updates for conversation
        read_all_data = {
            "conversation_id": self.test_data["conversation_id"]
        }
        self.test_endpoint("POST", "/api/status/read", read_all_data)
        
        # Test reading status updates filtered by agent type
        read_filtered_data = {
            "conversation_id": self.test_data["conversation_id"],
            "agent_type": "assistant"
        }
        self.test_endpoint("POST", "/api/status/read", read_filtered_data)
        
        # Test reading status updates filtered by specific agent
        read_agent_data = {
            "conversation_id": self.test_data["conversation_id"],
            "agent_type": "assistant",
            "agent_id": "test-agent-001"
        }
        self.test_endpoint("POST", "/api/status/read", read_agent_data)

    def _create_test_user(self):
        """Create a test user in the database for testing purposes"""
        import pymongo
        from datetime import datetime
        
        try:
            # Direct database insertion for testing
            # This is a workaround since there's no user creation endpoint
            from dbmanager import get_db_manager
            db_manager = get_db_manager()
            
            if db_manager.is_connected():
                test_user = {
                    "uid": self.test_data["user_id"],
                    "email": f"testuser_{self.test_data['user_id'][:8]}@example.com",
                    "created_at": datetime.utcnow(),
                    "Contacts": []
                }
                
                # Insert user if doesn't exist
                existing_user = db_manager.users.find_one({"uid": self.test_data["user_id"]})
                if not existing_user:
                    db_manager.users.insert_one(test_user)
                    print(f"📝 Created test user: {self.test_data['user_id'][:8]}...")
                else:
                    print(f"📝 Using existing test user: {self.test_data['user_id'][:8]}...")
            else:
                print("⚠️  Could not create test user - database not connected")
        except Exception as e:
            print(f"⚠️  Could not create test user: {str(e)}")

    def run_all_tests(self):
        """Run comprehensive test suite"""
        print("🚀 Starting Global Tools API Test Suite")
        print(f"Testing against: {self.base_url}")
        print("=" * 60)
        
        # Run all test categories
        self.run_basic_tests()
        database_available = self.run_database_tests()
        self.run_search_tests()
        
        if database_available:
            self.run_memory_tests()
            self.run_status_update_tests()
        
        self.run_vector_database_tests()
        
        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print test results summary"""
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if "✅" in r["status"]])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if "❌" in result["status"]:
                    print(f"  • {result['method']} {result['endpoint']} - {result['details']}")
        
        print("\n🔧 SERVICE STATUS:")
        
        # Analyze service availability
        services = {
            "API Server": any("GET /" == r["endpoint"] and "✅" in r["status"] for r in self.test_results),
            "MongoDB": any("/api/database/status" in r["endpoint"] and "✅" in r["status"] for r in self.test_results),
            "ChromaDB": any("/api/vector/status" in r["endpoint"] and "✅" in r["status"] for r in self.test_results),
            "Tavily Search": any("/api/search" in r["endpoint"] and "✅" in r["status"] for r in self.test_results)
        }
        
        for service, available in services.items():
            status = "🟢 Available" if available else "🔴 Unavailable"
            print(f"  • {service}: {status}")
        
        print("\n💡 RECOMMENDATIONS:")
        if not services["MongoDB"]:
            print("  • Start MongoDB service for database functionality")
        if not services["ChromaDB"]:
            print("  • Configure ChromaDB for vector database features")
        if not services["Tavily Search"]:
            print("  • Set TAVILY_API_KEY environment variable for web search")
        
        if failed_tests == 0:
            print("  • 🎉 All tests passed! Your API is fully functional.")

def main():
    """Main test runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Global Tools API")
    parser.add_argument("--url", default="http://localhost:8000", 
                       help="Base URL of the API (default: http://localhost:8000)")
    parser.add_argument("--verbose", action="store_true", 
                       help="Show detailed test output")
    
    args = parser.parse_args()
    
    # Test API connectivity first
    try:
        response = requests.get(f"{args.url}/", timeout=5)
        if response.status_code != 200:
            print(f"❌ API not responding at {args.url}")
            print("Make sure the server is running with: uvicorn main:app --reload")
            return
    except requests.exceptions.RequestException:
        print(f"❌ Cannot connect to API at {args.url}")
        print("Make sure the server is running with: uvicorn main:app --reload")
        return
    
    # Run tests
    tester = APITester(args.url)
    tester.run_all_tests()

if __name__ == "__main__":
    main() 