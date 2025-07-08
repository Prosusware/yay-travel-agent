 # Checkout Agent API

An automated booking service that uses AI agents to handle flight, hotel, and food delivery bookings through web automation.

## Features

- **Flight Booking**: Automated flight search and booking with customizable preferences
- **Hotel Booking**: Hotel search and reservation with location and budget constraints
- **Food Delivery**: Automated food ordering from delivery platforms
- **RESTful API**: FastAPI-based endpoints for easy integration
- **Cloud Ready**: Docker and Cloud Run deployment templates included

## API Endpoints

### Base URL
```
http://localhost:8080/api/v1
```

### Flight Booking
**POST** `/flights/book`

Book a flight with specified parameters.

**Request Schema:**
```json
{
  "initial_url": "string (optional)",
  "departure": "string (required)",
  "destination": "string (required)",
  "trip_type": "Round Trip | One Way (default: Round Trip)",
  "departure_date": "string (optional)",
  "return_date": "string (optional)",
  "budget": "string (optional)",
  "preferred_airlines": ["string"] (optional),
  "num_travelers": "integer (default: 1)",
  "traveler_info": {
    "first_name": "string (required)",
    "last_name": "string (required)",
    "email": "string (required)",
    "phone": "string (required)",
    "address": "string (required)",
    "city": "string (required)",
    "country": "string (required)"
  }
}
```

### Hotel Booking
**POST** `/hotels/book`

Book a hotel with specified parameters.

**Request Schema:**
```json
{
  "initial_url": "string (optional)",
  "city": "string (required)",
  "location_preference": "string (optional)",
  "check_in_date": "string (optional)",
  "check_out_date": "string (optional)",
  "budget": "string (optional)",
  "num_guests": "integer (optional)",
  "room_type": "string (optional)",
  "traveler_info": {
    "first_name": "string (required)",
    "last_name": "string (required)",
    "email": "string (required)",
    "phone": "string (required)",
    "address": "string (required)",
    "city": "string (required)",
    "country": "string (required)"
  }
}
```

### Food Delivery
**POST** `/food/book`

Order food delivery with specified parameters.

**Request Schema:**
```json
{
  "initial_url": "string (optional)",
  "cuisine": "string (required)",
  "dishes": ["string"] (optional),
  "delivery_address": "string (optional)",
  "max_eta": "string (optional)",
  "budget": "string (optional)",
  "delivery_info": {
    "first_name": "string (required)",
    "last_name": "string (required)",
    "email": "string (required)",
    "phone": "string (required)",
    "address": "string (required)",
    "city": "string (required)",
    "country": "string (required)"
  }
}
```

### Response Schema
All endpoints return the same response format:

```json
{
  "result": "string"
}
```

## Development Setup

### Prerequisites
- Python 3.11+
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Prosusware/checkout-agent
   cd checkout-agent
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   playwright install chromium --with-deps --no-shell
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env  # if available
   # Add your API keys and configuration
   ```

### Running Locally

1. **Start the development server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
   ```

2. **Access the API**
   - API: http://localhost:8080
   - Interactive docs: http://localhost:8080/docs
   - Health check: http://localhost:8080/health

### Example Usage

**Book a flight:**
```bash
curl -X POST http://localhost:8080/api/v1/flights/book \
  -H "Content-Type: application/json" \
  -d '{
    "departure": "San Francisco",
    "destination": "New York",
    "trip_type": "Round Trip",
    "departure_date": "2025-08-01",
    "return_date": "2025-08-10",
    "budget": "500",
    "traveler_info": {
      "first_name": "John",
      "last_name": "Doe",
      "email": "john@example.com",
      "phone": "+1234567890",
      "address": "123 Main St",
      "city": "San Francisco",
      "country": "USA"
    }
  }'
```

**Book a hotel:**
```bash
curl -X POST http://localhost:8080/api/v1/hotels/book \
  -H "Content-Type: application/json" \
  -d '{
    "city": "San Francisco",
    "location_preference": "Downtown",
    "check_in_date": "2025-08-01",
    "check_out_date": "2025-08-05",
    "budget": "200",
    "traveler_info": {
      "first_name": "John",
      "last_name": "Doe",
      "email": "john@example.com",
      "phone": "+1234567890",
      "address": "123 Main St",
      "city": "San Francisco",
      "country": "USA"
    }
  }'
```

## Deployment

### Docker
```bash
docker build -f docker/Dockerfile -t checkout-agent .
docker run -p 8080:8080 checkout-agent
```

### Google Cloud Run
1. **Build and push to Google Container Registry**
   ```bash
   gcloud builds submit --config docker/cloudbuild.yaml
   ```

2. **Deploy to Cloud Run**
   ```bash
   gcloud run deploy checkout-agent \
     --image gcr.io/PROJECT_ID/checkout-agent:latest \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

## Project Structure

```
checkout-agent/
├── app/
│   ├── api/
│   │   └── routes/
│   │       ├── flights.py      # Flight booking endpoints
│   │       ├── hotels.py       # Hotel booking endpoints
│   │       └── food.py         # Food delivery endpoints
│   ├── core/
│   │   └── config.py           # Configuration settings
│   ├── services/
│   │   ├── booking_agent.py    # Core booking logic
│   │   └── prompts.py          # AI prompts for different booking types
│   └── main.py                 # FastAPI application entry point
├── docker/
│   ├── Dockerfile              # Production Docker image
│   └── cloudbuild.yaml         # Google Cloud Build configuration
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Dependencies

- **FastAPI**: Web framework for building APIs
- **Uvicorn**: ASGI server for running FastAPI
- **Pydantic**: Data validation and settings management
- **Skyvern**: Web automation framework
- **Anthropic Claude and Gemini**: AI models for booking decisions

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

[Add your license information here]