# Global Tools API

A comprehensive API providing access to various external tools and services, including Tavily search integration and MongoDB database management. Built with FastAPI and deployed to Google Cloud Run.

## Features

- FastAPI web framework
- Tavily web search integration
- MongoDB database management (Prosusware database)
- Contact management system
- Memory storage and retrieval system
- ChromaDB vector database integration
- Remote embedding service support
- Docker containerization
- Google Cloud Run deployment
- Automatic CI/CD with Cloud Build
- Health check endpoint
- Production-ready configuration

## API Endpoints

- `GET /` - Welcome message
- `GET /health` - Health check with service status
- `GET /api/info` - Service information and available tools
- `GET /api/search?query={query}` - Tavily web search
- `GET /api/database/status` - MongoDB database status and statistics
- `POST /api/contacts/add` - Add contact (supports partial information)
- `PATCH /api/contacts/update` - Update existing contact with additional information
- `GET /api/contacts/{user_id}` - Get all contacts for a user (with completion status)
- `POST /api/memory/add` - Add a memory for a user or contact
- `POST /api/memory/search` - Search memories using natural language
- `GET /api/vector/status` - ChromaDB vector database status
- `GET /api/vector/collections` - List all vector collections
- `GET /api/vector/collections/{name}` - Get collection information
- `DELETE /api/vector/collections/{name}` - Delete a collection
- `POST /api/vector/documents/add` - Add documents to a collection
- `POST /api/vector/documents/query` - Query documents using semantic search
- `PATCH /api/vector/documents/update` - Update documents in a collection
- `DELETE /api/vector/documents/delete` - Delete documents from a collection

## MongoDB Database Integration

The API connects to a MongoDB database called **Prosusware** with the following collections:

### Collections:
1. **users** - User management and profiles
2. **tools** - Available tools and their configurations  
3. **sessions** - User session management
4. **analytics** - Usage analytics and metrics

### Database Features:
- Automatic connection management with reconnection
- Comprehensive error handling and logging
- Performance-optimized indexes on key fields
- Database statistics and health monitoring
- Connection pooling and timeout configuration

### Database Status Endpoint
```bash
curl "https://your-service-url/api/database/status"
```

Response format:
```json
{
  "status": "connected",
  "message": "Database connection active",
  "statistics": {
    "database_name": "Prosusware",
    "collections": {
      "users": {
        "name": "users",
        "document_count": 150,
        "indexes": 3
      },
      "tools": {
        "name": "tools", 
        "document_count": 25,
        "indexes": 4
      },
      "sessions": {
        "name": "sessions",
        "document_count": 45,
        "indexes": 5
      },
      "analytics": {
        "name": "analytics",
        "document_count": 1250,
        "indexes": 5
      }
    }
  }
}
```

## Tavily Search API

The `/api/search` endpoint provides web search capabilities using the Tavily API with advanced search depth, optimized for LLM consumption:

### Usage
```bash
curl "https://your-service-url/api/search?query=latest%20AI%20news"
```

### Response Format
The API returns a clean, formatted context string perfect for LLM consumption:

```json
{
  "query": "latest AI news",
  "context": "Direct Answer: The latest AI news includes major developments in...\n\nSearch Results:\n==================================================\n1. Major AI Breakthrough in 2024\n   URL: https://example.com/ai-breakthrough\n   Content: Scientists have announced a significant breakthrough in artificial intelligence...\n\n2. New AI Regulations Announced\n   URL: https://example.com/ai-regulations\n   Content: Government officials have released new guidelines for AI development...\n\n3. Tech Giants Invest in AI Research\n   URL: https://example.com/ai-investment\n   Content: Major technology companies are increasing their investment in AI research...",
  "source_count": 8
}
```

### Features
- **Advanced Search Depth**: Uses Tavily's advanced search for comprehensive results
- **LLM-Optimized**: Returns formatted context string ready for LLM consumption
- **Direct Answers**: Includes direct answers when available
- **Structured Results**: Clean formatting with numbered sources, URLs, and content
- **High Quality Sources**: Maximum 8 high-quality results per search

## Contact Management API

The Global Tools API provides comprehensive contact management functionality with support for partial contact information and progressive updates.

### Add Contact (Partial Information Supported)
`POST /api/contacts/add`

Add a new contact to a user's contact list. Only email is required - other fields are optional and can be added later.

#### Request Body
```json
{
  "UserID": "user-uuid-here",
  "contact": {
    "email": "gangevo@gmail.com"
  }
}
```

Or with complete information:
```json
{
  "UserID": "user-uuid-here",
  "contact": {
    "FirstName": "Fergus",
    "LastName": "McKenzie-Wilson",
    "nickname": "Ferg", 
    "email": "gangevo@gmail.com",
    "phoneNumber": "+447449313570"
  }
}
```

#### Response
```json
{
  "message": "Contact added successfully with partial information",
  "contact": {
    "uid": "contact-uuid-generated",
    "FirstName": null,
    "LastName": null,
    "nickname": null,
    "email": "gangevo@gmail.com", 
    "phoneNumber": null,
    "created_at": "2024-01-15T10:30:00.000Z",
    "updated_at": null
  },
  "user_id": "user-uuid-here",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "note": "You can update this contact later with additional information using the update endpoint"
}
```

### Update Contact
`PATCH /api/contacts/update`

Update an existing contact with additional or modified information.

#### Request Body
```json
{
  "UserID": "user-uuid-here",
  "contact_uid": "contact-uuid-here",
  "contact": {
    "FirstName": "Fergus",
    "LastName": "McKenzie-Wilson",
    "nickname": "Ferg",
    "phoneNumber": "+447449313570"
  }
}
```

#### Response
```json
{
  "message": "Contact updated successfully",
  "contact": {
    "uid": "contact-uuid-here",
    "FirstName": "Fergus",
    "LastName": "McKenzie-Wilson",
    "nickname": "Ferg",
    "email": "gangevo@gmail.com",
    "phoneNumber": "+447449313570", 
    "created_at": "2024-01-15T10:30:00.000Z",
    "updated_at": "2024-01-15T11:15:00.000Z"
  },
  "user_id": "user-uuid-here",
  "fields_updated": ["Contacts.$.FirstName", "Contacts.$.LastName", "Contacts.$.nickname", "Contacts.$.phoneNumber", "Contacts.$.updated_at"],
  "timestamp": "2024-01-15T11:15:00.000Z"
}
```

#### Features
- **Partial Information Support**: Only email is required when adding contacts
- **Progressive Updates**: Add missing information over time
- **Automatic UID Generation**: Each contact gets a unique identifier
- **Email Validation**: Ensures email addresses are properly formatted
- **Duplicate Prevention**: Prevents adding contacts with duplicate emails for the same user
- **User Validation**: Verifies the user exists before adding/updating contacts
- **Timestamp Tracking**: Records creation and update times
- **Field Validation**: Ensures no empty strings are saved for optional fields (FirstName, LastName, nickname, phoneNumber)
- **Nickname Support**: Optional nickname field for casual contact identification

### Get User Contacts (Enhanced)
`GET /api/contacts/{user_id}`

Retrieve all contacts for a specific user with completion status information.

#### Response
```json
{
  "user_id": "user-uuid-here",
  "contacts": [
    {
      "uid": "contact-uuid-1",
      "FirstName": null,
      "LastName": null,
      "nickname": null, 
      "email": "partial@example.com",
      "phoneNumber": null,
      "created_at": "2024-01-15T10:30:00.000Z",
      "missing_fields": ["FirstName", "LastName", "phoneNumber"]
    },
    {
      "uid": "contact-uuid-2",
      "FirstName": "Fergus",
      "LastName": "McKenzie-Wilson",
      "nickname": "Ferg",
      "email": "gangevo@gmail.com",
      "phoneNumber": "+447449313570",
      "created_at": "2024-01-15T10:30:00.000Z",
      "updated_at": "2024-01-15T11:15:00.000Z"
    }
  ],
  "total_contacts": 2,
  "complete_contacts": 1,
  "partial_contacts": 1,
  "timestamp": "2024-01-15T11:30:00.000Z"
}
```

### Usage Examples

#### Add Partial Contact
```bash
curl -X POST "https://your-service-url/api/contacts/add" \
  -H "Content-Type: application/json" \
  -d '{
    "UserID": "user-uuid-here",
    "contact": {
      "email": "gangevo@gmail.com"
    }
  }'
```

#### Update Contact with Additional Information
```bash
curl -X PATCH "https://your-service-url/api/contacts/update" \
  -H "Content-Type: application/json" \
  -d '{
    "UserID": "user-uuid-here",
    "contact_uid": "contact-uuid-here",
    "contact": {
      "FirstName": "Fergus",
      "LastName": "McKenzie-Wilson",
      "nickname": "Ferg",
      "phoneNumber": "+447449313570"
    }
  }'
```

#### Add Complete Contact
```bash
curl -X POST "https://your-service-url/api/contacts/add" \
  -H "Content-Type: application/json" \
  -d '{
    "UserID": "user-uuid-here",
    "contact": {
      "FirstName": "Fergus",
      "LastName": "McKenzie-Wilson",
      "nickname": "Ferg",
      "email": "gangevo@gmail.com", 
      "phoneNumber": "+447449313570"
    }
  }'
```

### Workflow Examples

#### Progressive Contact Building
1. **Initial Contact**: Add with just email
2. **Add Name**: Update with FirstName and LastName
3. **Add Phone**: Update with phoneNumber
4. **Modify Email**: Update email address if needed

### Error Handling
- **400**: Invalid data, missing required fields, empty strings
- **404**: User not found, contact not found
- **409**: Contact with email already exists for user
- **422**: Invalid email format or validation errors
- **503**: Database connection unavailable

## Memory Management System

The Global Tools API provides intelligent memory storage and retrieval functionality that allows users to store and search through personal memories and contact-specific memories using natural language.

### Features
- **User Memories**: Store personal memories associated with a user
- **Contact Memories**: Store memories associated with specific contacts
- **Natural Language Search**: Search memories using conversational queries
- **Semantic Similarity**: Find relevant memories based on meaning, not just keywords
- **Email Lookup**: Reference contacts by email address for convenience
- **Cross-Collection Search**: Search across user's personal memories and all their contact memories (user-scoped only)

### Memory Storage Logic
- **User Memory**: Collection name = `user_id` (when no contact specified)
- **Contact Memory**: Collection name = `contact_id` (when contact specified)
- **Email Resolution**: Email addresses are automatically resolved to contact IDs
- **Auto-Creation**: Collections are created automatically if they don't exist

### Memory Management Endpoints

#### Memory Management
- `POST /api/memory/add` - Add memories to vector database (user or contact-specific)
- `POST /api/memory/search` - Search memories using natural language queries

#### Status Update Management
- `POST /api/status/write` - Write status updates to the database
- `POST /api/status/read` - Read status updates with filtering options

### Status Update Management

The Global Tools API includes a status update system for tracking agent activities and updates during conversations. This system is designed for multi-agent applications where different agents need to log their status and activities.

#### Write Status Update
`POST /api/status/write`

Store a status update from an agent for a specific conversation.

##### Request Example
```bash
curl -X POST "https://your-service-url/api/status/write" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "agent-assistant-001",
    "agent_type": "assistant",
    "conversation_id": "conv-uuid-12345",
    "update": "Successfully processed user query about renewable energy. Generated 3 research suggestions and initiated web search."
  }'
```

##### Response
```json
{
  "message": "Status update successfully written",
  "status_update_id": "status-uuid-generated",
  "agent_id": "agent-assistant-001",
  "agent_type": "assistant",
  "conversation_id": "conv-uuid-12345",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

#### Read Status Updates
`POST /api/status/read`

Retrieve status updates for a conversation with optional filtering by agent type and agent ID.

##### Read All Updates for a Conversation
```bash
curl -X POST "https://your-service-url/api/status/read" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "conv-uuid-12345"
  }'
```

##### Filter by Agent Type
```bash
curl -X POST "https://your-service-url/api/status/read" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "conv-uuid-12345",
    "agent_type": "assistant"
  }'
```

##### Filter by Specific Agent
```bash
curl -X POST "https://your-service-url/api/status/read" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "conv-uuid-12345",
    "agent_type": "assistant",
    "agent_id": "agent-assistant-001"
  }'
```

##### Response
```json
{
  "conversation_id": "conv-uuid-12345",
  "agent_type": "assistant",
  "agent_id": "agent-assistant-001",
  "status_updates": [
    {
      "id": "status-uuid-1",
      "agent_id": "agent-assistant-001",
      "agent_type": "assistant",
      "conversation_id": "conv-uuid-12345",
      "update": "Successfully processed user query about renewable energy. Generated 3 research suggestions and initiated web search.",
      "timestamp": "2024-01-15T10:30:00.000Z"
    },
    {
      "id": "status-uuid-2",
      "agent_id": "agent-assistant-001",
      "agent_type": "assistant",
      "conversation_id": "conv-uuid-12345",
      "update": "Completed web search and compiled research results. Found 15 relevant articles and 3 academic papers.",
      "timestamp": "2024-01-15T10:32:15.000Z"
    }
  ],
  "total_results": 2,
  "timestamp": "2024-01-15T10:35:00.000Z"
}
```

#### Filtering Options
- **conversation_id** (required): Only return updates for this specific conversation
- **agent_type** (optional): Filter by agent type (e.g., "assistant", "researcher", "validator")  
- **agent_id** (optional): Filter by specific agent identifier

#### Use Cases
1. **Conversation Tracking**: Monitor all agent activities during a conversation
2. **Agent Debugging**: Track specific agent behavior and decision points
3. **Performance Analysis**: Analyze agent performance and response patterns
4. **Audit Trail**: Maintain detailed logs of agent actions for compliance
5. **Multi-Agent Coordination**: Coordinate between multiple agents in complex workflows

#### Data Storage
- Status updates are stored in the MongoDB collection `Status_updates`
- Each update includes automatic timestamp generation
- Updates are sorted chronologically (oldest first) when retrieved
- No automatic cleanup - implement retention policies as needed

#### Validation Rules
- **agent_id**: 1-100 characters, required
- **agent_type**: 1-50 characters, required  
- **conversation_id**: 1-100 characters, required
- **update**: 1-5000 characters, required

#### Error Handling
- **400**: Invalid or missing required fields, validation errors
- **500**: Database insert/query errors
- **503**: MongoDB connection unavailable

## ChromaDB Vector Database Integration

The API provides comprehensive vector database functionality using ChromaDB for semantic search, document storage, and retrieval operations.

### Features
- **Document Storage**: Store and embed text documents with metadata
- **Semantic Search**: Query documents using natural language with vector similarity
- **Collection Management**: Create, list, and delete document collections
- **Remote Embeddings**: Support for external embedding services
- **Metadata Filtering**: Filter documents by metadata during queries
- **Batch Operations**: Add, update, and delete multiple documents at once

### Environment Variables
- `CHROMA_HOST`: ChromaDB server host (default: localhost)
- `CHROMA_PORT`: ChromaDB server port (default: 8000)
- `EMBEDDING_SERVICE_URL`: Remote embedding service URL (optional)

### Vector Database Endpoints

#### Check Status
`GET /api/vector/status`

Get ChromaDB connection status and statistics.

```bash
curl "https://your-service-url/api/vector/status"
```

Response:
```json
{
  "status": "connected",
  "message": "ChromaDB is operational", 
  "host": "localhost",
  "port": 8000,
  "embedding_service": "http://localhost:5000",
  "embedding_function_available": true,
  "collection_count": 3,
  "collections": ["documents", "knowledge_base", "user_data"]
}
```

#### List Collections
`GET /api/vector/collections`

List all available collections.

```bash
curl "https://your-service-url/api/vector/collections"
```

Response:
```json
{
  "collections": ["documents", "knowledge_base", "user_data"],
  "collection_count": 3,
  "connection_status": "connected",
  "host": "localhost",
  "port": 8000
}
```

#### Get Collection Info
`GET /api/vector/collections/{collection_name}`

Get detailed information about a specific collection.

```bash
curl "https://your-service-url/api/vector/collections/documents"
```

Response:
```json
{
  "name": "documents",
  "document_count": 150,
  "metadata": {"description": "Company documents", "created": "2024-01-15"},
  "embedding_function_available": true
}
```

#### Add Documents
`POST /api/vector/documents/add`

Add documents to a collection with automatic embedding.

```bash
curl -X POST "https://your-service-url/api/vector/documents/add" \
  -H "Content-Type: application/json" \
  -d '{
    "collection_name": "documents",
    "documents": [
      "This is the first document about AI",
      "This is the second document about machine learning"
    ],
    "ids": ["doc1", "doc2"],
    "metadatas": [
      {"category": "AI", "author": "John"},
      {"category": "ML", "author": "Jane"}
    ]
  }'
```

Response:
```json
{
  "message": "Successfully added 2 documents to collection 'documents'",
  "collection": "documents",
  "document_count": 2,
  "ids": ["doc1", "doc2"],
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

#### Query Documents
`POST /api/vector/documents/query`

Search documents using semantic similarity.

```bash
curl -X POST "https://your-service-url/api/vector/documents/query" \
  -H "Content-Type: application/json" \
  -d '{
    "collection_name": "documents",
    "query_texts": ["artificial intelligence research"],
    "n_results": 5,
    "where": {"category": "AI"},
    "include": ["documents", "metadatas", "distances"]
  }'
```

Response:
```json
{
  "query_texts": ["artificial intelligence research"],
  "collection": "documents",
  "results": {
    "ids": [["doc1", "doc3"]],
    "documents": [["This is the first document about AI", "Advanced AI research paper"]],
    "metadatas": [[{"category": "AI", "author": "John"}, {"category": "AI", "author": "Alice"}]],
    "distances": [[0.1, 0.3]]
  },
  "result_count": 2,
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

#### Update Documents
`PATCH /api/vector/documents/update`

Update existing documents or their metadata.

```bash
curl -X PATCH "https://your-service-url/api/vector/documents/update" \
  -H "Content-Type: application/json" \
  -d '{
    "collection_name": "documents",
    "ids": ["doc1"],
    "documents": ["Updated document about artificial intelligence"],
    "metadatas": [{"category": "AI", "author": "John", "updated": "2024-01-15"}]
  }'
```

#### Delete Documents
`DELETE /api/vector/documents/delete`

Remove documents from a collection.

```bash
curl -X DELETE "https://your-service-url/api/vector/documents/delete" \
  -H "Content-Type: application/json" \
  -d '{
    "collection_name": "documents",
    "ids": ["doc1", "doc2"]
  }'
```

#### Delete Collection
`DELETE /api/vector/collections/{collection_name}`

Delete an entire collection and all its documents.

```bash
curl -X DELETE "https://your-service-url/api/vector/collections/documents"
```

### Remote Embedding Service

The ChromaDB integration supports an external embedding service for generating document embeddings. The service should implement the following interface:

#### Embedding Service API
- `GET /` - Health check endpoint
- `POST /embed` - Generate embeddings for text

Request format:
```json
{
  "texts": ["document 1", "document 2"]
}
```

Response format:
```json
{
  "embeddings": [[0.1, 0.2, ...], [0.3, 0.4, ...]]
}
```

## Environment Variables

The application uses the following environment variables:

- `PORT`: Server port (default: 8080)
- `ENVIRONMENT`: Environment name (default: production)
- `TAVILY_API_KEY`: **Required** - Your Tavily API key
- `MONGODB_URL`: **Required** - MongoDB connection string
- `CHROMA_HOST`: ChromaDB server host (default: localhost)
- `CHROMA_PORT`: ChromaDB server port (default: 8000)
- `CHROMA_SERVER_AUTHN_CREDENTIALS`: ChromaDB authentication credentials (optional)
- `EMBEDDING_SERVICE_URL`: Remote embedding service URL (optional)

## Local Development

1. **Get API Keys and Services**:
   - Tavily API key from [Tavily](https://tavily.com/)
   - MongoDB connection string (local MongoDB or MongoDB Atlas)
   - ChromaDB server (local installation or hosted service)
   - Optional: Remote embedding service

2. **Set environment variables**:
   ```bash
   export TAVILY_API_KEY="your-tavily-api-key"
   export MONGODB_URL="mongodb://localhost:27017"
   # or for MongoDB Atlas:
   # export MONGODB_URL="mongodb+srv://username:password@cluster.mongodb.net"
   
   # ChromaDB configuration
   export CHROMA_HOST="localhost"
   export CHROMA_PORT="8000"
   export CHROMA_SERVER_AUTHN_CREDENTIALS="your-chroma-auth-token"  # optional
   
   # Optional: Remote embedding service
   export EMBEDDING_SERVICE_URL="http://localhost:5000"
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   python main.py
   ```

5. **Open http://localhost:8080 in your browser**

## Docker Build & Run

1. Build the Docker image:
   ```bash
   docker build -t global-tools-api .
   ```

2. Run the container with environment variables:
   ```bash
   docker run -p 8080:8080 \
     -e TAVILY_API_KEY="your-api-key" \
     -e MONGODB_URL="your-mongodb-url" \
     -e CHROMA_HOST="your-chroma-host" \
     -e CHROMA_PORT="8000" \
     -e CHROMA_SERVER_AUTHN_CREDENTIALS="your-chroma-auth-token" \
     -e EMBEDDING_SERVICE_URL="your-embedding-service-url" \
     global-tools-api
   ```

## GCP Cloud Run Deployment

### Prerequisites

1. Install the Google Cloud SDK
2. Get required credentials and services:
   - Tavily API key from [Tavily](https://tavily.com/)
   - MongoDB connection string (MongoDB Atlas recommended for production)
   - ChromaDB server endpoint (hosted ChromaDB service recommended for production)
   - Optional: Remote embedding service URL
3. Authenticate with Google Cloud:
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```
4. Enable required APIs:
   ```bash
   gcloud services enable cloudbuild.googleapis.com
   gcloud services enable run.googleapis.com
   gcloud services enable containerregistry.googleapis.com
   ```

### Manual Deployment

1. Build and push the image:
   ```bash
   gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/global-tools-api
   ```

2. Deploy to Cloud Run:
   ```bash
   gcloud run deploy global-tools-api \
     --image gcr.io/YOUR_PROJECT_ID/global-tools-api \
     --platform managed \
     --region europe-west1 \
     --allow-unauthenticated \
     --set-env-vars TAVILY_API_KEY=your-tavily-api-key,MONGODB_URL=your-mongodb-url,CHROMA_HOST=your-chroma-host,CHROMA_PORT=8000,CHROMA_SERVER_AUTHN_CREDENTIALS=your-chroma-auth-token,EMBEDDING_SERVICE_URL=your-embedding-service-url
   ```

### Automated Deployment with Cloud Build

1. Connect your repository to Cloud Build
2. Set up substitution variables in Cloud Build:
   - `_TAVILY_API_KEY`: Your Tavily API key
   - `_MONGODB_URL`: Your MongoDB connection string
   - `_CHROMA_HOST`: Your ChromaDB server host
   - `_CHROMA_PORT`: ChromaDB server port (default: 8000)
   - `_CHROMA_SERVER_AUTHN_CREDENTIALS`: ChromaDB authentication credentials (optional)
   - `_EMBEDDING_SERVICE_URL`: Remote embedding service URL (optional)
3. Create a trigger that runs on push to main branch
4. The `cloudbuild.yaml` file will automatically build and deploy your application

#### Setting up Cloud Build Variables

In the Google Cloud Console:
1. Go to Cloud Build > Triggers
2. Create or edit your trigger
3. Add substitution variables:
   - Variable name: `_TAVILY_API_KEY`, Value: `your-tavily-api-key`
   - Variable name: `_MONGODB_URL`, Value: `your-mongodb-connection-string`
   - Variable name: `_CHROMA_HOST`, Value: `your-chroma-host`
   - Variable name: `_CHROMA_PORT`, Value: `8000`
   - Variable name: `_CHROMA_SERVER_AUTHN_CREDENTIALS`, Value: `your-chroma-auth-token` (optional)
   - Variable name: `_EMBEDDING_SERVICE_URL`, Value: `your-embedding-service-url` (optional)

### Configuration

You can modify the following settings in `cloudbuild.yaml`:

- Region: Currently set to `europe-west1`
- Memory: Adjust the `--memory` parameter
- CPU: Adjust the `--cpu` parameter
- Max instances: Change `--max-instances` value
- Authentication: Remove `--allow-unauthenticated` to require authentication

## Testing

The project includes comprehensive testing tools to verify all API endpoints and service connections.

### ChromaDB Connection Test

Before running the full API, test your ChromaDB connection:

```bash
# Test ChromaDB connection with authentication
python3 test_chroma.py
```

This will:
- Verify all required environment variables are set
- Test the authenticated connection to ChromaDB
- Validate basic operations (list collections, create/delete test collection)
- Provide detailed troubleshooting information if connection fails

### Full API Test Suite

Test all API endpoints:

```bash
# Option 1: Automated test runner (recommended)
./run_tests.sh

# Option 2: Manual approach
# Start API server first
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Then run tests in another terminal
python3 test_api.py
```

The test suite will:
- Test all 20+ API endpoints
- Check service availability (MongoDB, ChromaDB, Tavily)
- Provide detailed success/failure reports
- Show response times and error details
- Give recommendations for fixing issues

### Test Dependencies

```bash
# Install test dependencies
pip install -r test_requirements.txt
```

## Adding New Tools

To add new external tools/APIs:

1. Add the client library to `requirements.txt`
2. Initialize the client in `main.py`
3. Create new endpoints following the pattern of `/api/search`
4. Update the `available_tools` list in `/api/info`
5. Add documentation to this README

## Database Collections Schema

### Users Collection
```json
{
  "_id": "ObjectId",
  "uid": "user-uuid-string",
  "email": "user@example.com",
  "name": "John Doe",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "last_login": "2024-01-15T10:30:00Z",
  "Contacts": [
    {
      "uid": "contact-uuid-1",
      "FirstName": "Fergus",
      "LastName": "McKenzie-Wilson",
      "nickname": "Ferg", 
      "email": "gangevo@gmail.com",
      "phoneNumber": "+447449313570",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T11:15:00Z"
    },
    {
      "uid": "contact-uuid-2",
      "FirstName": null,
      "LastName": null,
      "nickname": null,
      "email": "partial@example.com",
      "phoneNumber": null,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### Tools Collection
```json
{
  "_id": "ObjectId", 
  "name": "tool_name",
  "category": "search",
  "description": "Tool description",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Sessions Collection
```json
{
  "_id": "ObjectId",
  "session_id": "uuid",
  "user_id": "ObjectId",
  "created_at": "2024-01-01T00:00:00Z",
  "expires_at": "2024-01-01T01:00:00Z"
}
```

### Analytics Collection
```json
{
  "_id": "ObjectId",
  "event_type": "search_performed",
  "user_id": "ObjectId", 
  "data": {},
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## Project Structure

```
.
├── main.py               # FastAPI application with route definitions
├── models.py             # Pydantic models for request/response validation
├── validation.py         # Common validation utilities
├── contact_service.py    # Contact management business logic
├── search_service.py     # Tavily search service
├── memory_service.py     # Memory storage and retrieval business logic
├── status_service.py     # Status update management business logic
├── chroma_service.py     # ChromaDB vector database service
├── health_service.py     # Health monitoring and status services
├── dbmanager.py          # MongoDB database manager
├── chromaManager.py      # ChromaDB connection and operations manager
├── test_api.py           # Comprehensive API test suite
├── test_chroma.py        # ChromaDB connection test script
├── test_requirements.txt # Test dependencies
├── run_tests.sh          # Automated test runner script
├── requirements.txt      # Python dependencies
├── Dockerfile            # Container configuration
├── cloudbuild.yaml       # Cloud Build configuration
├── .gitignore            # Git ignore rules
└── README.md             # Documentation
```