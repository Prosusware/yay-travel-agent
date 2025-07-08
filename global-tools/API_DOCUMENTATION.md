# Global Tools API Documentation

This document provides a comprehensive guide to using the Global Tools API. It includes details on each endpoint, required parameters, and example requests using `curl`.

## General API Endpoints

### 1. Root

- **Method:** `GET`
- **Path:** `/`
- **Description:** Provides a welcome message and a summary of the API's features and available endpoints.
- **`curl` Example:**
  ```bash
  curl -X GET "https://<your-api-url>/"
  ```
- **Success Response:**
  A JSON object with a welcome message and API overview.

### 2. Service Information

- **Method:** `GET`
- **Path:** `/api/info`
- **Description:** Retrieves detailed information about the service, including its version, environment, and the status of its database connection.
- **`curl` Example:**
  ```bash
  curl -X GET "https://<your-api-url>/api/info"
  ```
- **Success Response:**
  A `ServiceInfoResponse` JSON object.

### 3. Web Search

- **Method:** `GET`
- **Path:** `/api/search`
- **Description:** Performs a web search using the Tavily API and returns results formatted for an LLM.
- **`curl` Example:**
  ```bash
  curl -X GET "https://<your-api-url>/api/search?query=latest%20AI%20developments"
  ```
- **Query Parameters:**
  - `query` (string, required): The search term.
- **Success Response:**
  A `SearchResponse` JSON object containing the formatted search context.

### 4. Database Status

- **Method:** `GET`
- **Path:** `/api/database/status`
- **Description:** Gets the connection status and statistics for the MongoDB database.
- **`curl` Example:**
  ```bash
  curl -X GET "https://<your-api-url>/api/database/status"
  ```
- **Success Response:**
  A `DatabaseStatsResponse` JSON object.

---

## Contact Management

### 1. Add Contact

- **Method:** `POST`
- **Path:** `/api/contacts/add`
- **Description:** Adds a new contact to a user's contact list. Only an email is required to start, and more details can be added later.
- **`curl` Example:**
  ```bash
  curl -X POST "https://<your-api-url>/api/contacts/add" \
  -H "Content-Type: application/json" \
  -d '{
    "UserID": "user_123",
    "contact": {
      "email": "jane.doe@example.com",
      "FirstName": "Jane",
      "LastName": "Doe"
    }
  }'
  ```
- **Request Body (`AddContactRequest`):**
  - `UserID` (string, required): The ID of the user adding the contact.
  - `contact` (object, required):
    - `email` (string, required): The contact's email address.
    - `FirstName` (string, optional)
    - `LastName` (string, optional)
    - `nickname` (string, optional)
    - `phoneNumber` (string, optional)
- **Success Response:**
  A JSON object confirming the contact was added, including the new `contact_uid`.

### 2. Update Contact

- **Method:** `PATCH`
- **Path:** `/api/contacts/update`
- **Description:** Updates an existing contact's information. At least one field in the `contact` object must be provided.
- **`curl` Example:**
  ```bash
  curl -X PATCH "https://<your-api-url>/api/contacts/update" \
  -H "Content-Type: application/json" \
  -d '{
    "UserID": "user_123",
    "contact_uid": "contact_abc",
    "contact": {
      "phoneNumber": "+1234567890"
    }
  }'
  ```
- **Request Body (`UpdateContactRequest`):**
  - `UserID` (string, required): The ID of the user.
  - `contact_uid` (string, required): The unique ID of the contact to update.
  - `contact` (object, required): An object containing the fields to update.
- **Success Response:**
  A JSON object confirming the update.

### 3. Get User Contacts

- **Method:** `GET`
- **Path:** `/api/contacts/{user_id}`
- **Description:** Retrieves all contacts for a specific user.
- **`curl` Example:**
  ```bash
  curl -X GET "https://<your-api-url>/api/contacts/user_123"
  ```
- **Path Parameters:**
  - `user_id` (string, required): The ID of the user whose contacts to retrieve.
- **Success Response:**
  A JSON array of contact objects.

---

## User Management

### 1. Get User

- **Method:** `GET`
- **Path:** `/api/user/{user_id}`
- **Description:** Retrieves a single user's profile by their ID.
- **`curl` Example:**
  ```bash
  curl -X GET "https://<your-api-url>/api/user/user_123"
  ```
- **Path Parameters:**
  - `user_id` (string, required): The ID of the user to retrieve.
- **Success Response:**
  A `UserResponse` JSON object.

---

## Conversation Management

### 1. Update Conversation Name

- **Method:** `PATCH`
- **Path:** `/api/conversations/name`
- **Description:** Updates the name of an existing conversation.
- **`curl` Example:**
  ```bash
  curl -X PATCH "https://<your-api-url>/api/conversations/name" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "conv_abc",
    "name": "New Conversation Title"
  }'
  ```
- **Request Body (`UpdateConversationNameRequest`):**
  - `conversation_id` (string, required): The ID of the conversation to update.
  - `name` (string, required): The new name for the conversation.
- **Success Response:**
  An `UpdateConversationNameResponse` JSON object confirming the change.

---

## Memory Management

### 1. Add Memory

- **Method:** `POST`
- **Path:** `/api/memory/add`
- **Description:** Adds a memory for a user or a contact. The memory is stored in a vector database for semantic search.
- **`curl` Example:**
  ```bash
  curl -X POST "https://<your-api-url>/api/memory/add" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "memory": "Jane Doe prefers morning meetings.",
    "contact_id": "contact_abc"
  }'
  ```
- **Request Body (`AddMemoryRequest`):**
  - `user_id` (string, required): The ID of the user this memory belongs to.
  - `memory` (string, required): The text of the memory.
  - `contact_id` (string, optional): The ID of a contact to associate with the memory.
  - `email` (string, optional): The email of a contact to associate with the memory.
- **Success Response:**
  An `AddMemoryResponse` JSON object.

### 2. Search Memory

- **Method:** `POST`
- **Path:** `/api/memory/search`
- **Description:** Searches memories using a natural language query.
- **`curl` Example:**
  ```bash
  curl -X POST "https://<your-api-url>/api/memory/search" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "query": "What are Jane Does preferences?"
  }'
  ```
- **Request Body (`SearchMemoryRequest`):**
  - `user_id` (string, required): The user whose memories to search.
  - `query` (string, required): The natural language search query.
  - `n_results` (integer, optional, default: 10): The number of results to return.
  - `search_all_collections` (boolean, optional, default: false): Whether to search across all of the user's collections.
- **Success Response:**
  A `SearchMemoryResponse` JSON object containing a list of relevant memories.

---

## Status Updates

### 1. Write Status Update

- **Method:** `POST`
- **Path:** `/api/status/write`
- **Description:** Writes a status update for a given agent and conversation.
- **`curl` Example:**
  ```bash
  curl -X POST "https://<your-api-url>/api/status/write" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "agent_xyz",
    "agent_type": "DataProcessor",
    "conversation_id": "conv_abc",
    "update": "Processing of dataset X has started."
  }'
  ```
- **Request Body (`WriteStatusUpdateRequest`):**
  - `agent_id` (string, required)
  - `agent_type` (string, required)
  - `conversation_id` (string, required)
  - `update` (string, required)
- **Success Response:**
  A `WriteStatusUpdateResponse` JSON object.

### 2. Read Status Updates

- **Method:** `POST`
- **Path:** `/api/status/read`
- **Description:** Reads status updates for a conversation, with optional filters.
- **`curl` Example:**
  ```bash
  curl -X POST "https://<your-api-url>/api/status/read" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "conv_abc",
    "agent_type": "DataProcessor"
  }'
  ```
- **Request Body (`ReadStatusUpdatesRequest`):**
  - `conversation_id` (string, required)
  - `agent_type` (string, optional)
  - `agent_id` (string, optional)
- **Success Response:**
  A `ReadStatusUpdatesResponse` JSON object with a list of matching status updates.

## Programming Language Examples

### Python Example

```python
import requests
import json

class GlobalToolsClient:
    def __init__(self, base_url="https://global-tools-api-534113739138.europe-west1.run.app"):
        self.base_url = base_url
    
    def health_check(self):
        response = requests.get(f"{self.base_url}/health")
        return response.json()
    
    def search_web(self, query):
        response = requests.get(f"{self.base_url}/api/search", 
                              params={"query": query})
        return response.json()
    
    def add_contact(self, user_id, contact_data):
        payload = {
            "UserID": user_id,
            "contact": contact_data
        }
        response = requests.post(f"{self.base_url}/api/contacts/add",
                               json=payload)
        return response.json()
    
    def add_memory(self, user_id, memory, contact_id=None):
        payload = {
            "user_id": user_id,
            "memory": memory
        }
        if contact_id:
            payload["contact_id"] = contact_id
            
        response = requests.post(f"{self.base_url}/api/memory/add",
                               json=payload)
        return response.json()
    
    def search_memory(self, user_id, query, n_results=10):
        payload = {
            "user_id": user_id,
            "query": query,
            "n_results": n_results
        }
        response = requests.post(f"{self.base_url}/api/memory/search",
                               json=payload)
        return response.json()

# Usage
client = GlobalToolsClient()

# Check health
health = client.health_check()
print(f"API Status: {health['status']}")

# Search web
search_result = client.search_web("latest Python frameworks")
print(f"Search context: {search_result['context'][:100]}...")

# Add contact
contact = {
    "email": "jane.doe@example.com",
    "FirstName": "Jane",
    "LastName": "Doe"
}
result = client.add_contact("user-123", contact)
print(f"Contact added: {result}")
```

### JavaScript/Node.js Example

```javascript
const axios = require('axios');

class GlobalToolsClient {
    constructor(baseUrl = 'https://global-tools-api-534113739138.europe-west1.run.app') {
        this.baseUrl = baseUrl;
    }

    async healthCheck() {
        const response = await axios.get(`${this.baseUrl}/health`);
        return response.data;
    }

    async searchWeb(query) {
        const response = await axios.get(`${this.baseUrl}/api/search`, {
            params: { query }
        });
        return response.data;
    }

    async addContact(userId, contactData) {
        const payload = {
            UserID: userId,
            contact: contactData
        };
        const response = await axios.post(`${this.baseUrl}/api/contacts/add`, payload);
        return response.data;
    }

    async addMemory(userId, memory, contactId = null) {
        const payload = {
            user_id: userId,
            memory: memory
        };
        if (contactId) {
            payload.contact_id = contactId;
        }
        
        const response = await axios.post(`${this.baseUrl}/api/memory/add`, payload);
        return response.data;
    }

    async searchMemory(userId, query, nResults = 10) {
        const payload = {
            user_id: userId,
            query: query,
            n_results: nResults
        };
        const response = await axios.post(`${this.baseUrl}/api/memory/search`, payload);
        return response.data;
    }
}

// Usage
const client = new GlobalToolsClient();

async function example() {
    try {
        // Check health
        const health = await client.healthCheck();
        console.log(`API Status: ${health.status}`);

        // Search web
        const searchResult = await client.searchWeb('latest JavaScript frameworks');
        console.log(`Search context: ${searchResult.context.substring(0, 100)}...`);

        // Add contact
        const contact = {
            email: 'john.smith@example.com',
            FirstName: 'John',
            LastName: 'Smith'
        };
        const result = await client.addContact('user-456', contact);
        console.log('Contact added:', result);
    } catch (error) {
        console.error('Error:', error.response?.data || error.message);
    }
}

example();
```

## Error Handling

The API returns structured error responses:

```json
{
  "error": "Error Type",
  "message": "Human readable error message",
  "details": "Additional error details",
  "endpoint": "/api/endpoint/path"
}
```

Common HTTP status codes:
- `200`: Success
- `400`: Bad Request (validation errors)
- `404`: Not Found
- `422`: Unprocessable Entity (validation errors)
- `500`: Internal Server Error

## Environment Setup

### Required Environment Variables

```bash
# MongoDB
MONGODB_URL=mongodb://localhost:27017/global_tools

# Tavily Search API
TAVILY_API_KEY=your_tavily_api_key

# ChromaDB Configuration
CHROMA_HOST=localhost
CHROMA_PORT=8000
CHROMA_AUTH_TOKEN=your_auth_token  # Optional

# Embedding Service
EMBEDDING_API_URL=http://localhost:8080/api/embedding/generate
```

### Docker Setup

1. **Run the API with Docker:**
```bash
docker build -t global-tools-api .
docker run -p 8000:8000 --env-file .env global-tools-api
```

2. **Using Docker Compose:**
```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MONGODB_URL=mongodb://mongo:27017/global_tools
      - TAVILY_API_KEY=${TAVILY_API_KEY}
    depends_on:
      - mongo
  
  mongo:
    image: mongo:latest
    ports:
      - "27017:27017"
```

## Testing

Run the comprehensive test suite:

```bash
python test_api.py --url https://global-tools-api-534113739138.europe-west1.run.app --verbose
```

This will test all endpoints and provide a detailed report of API functionality.

## Rate Limits

Currently, there are no rate limits imposed by the API itself. However, external services (Tavily, embedding service) may have their own rate limits.

## Support

For issues or questions, check the logs or run the health endpoints to diagnose service status. The `/health` and `/api/info` endpoints provide comprehensive service status information. 