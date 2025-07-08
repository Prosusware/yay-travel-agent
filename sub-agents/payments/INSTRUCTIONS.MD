# Checkout Agent API - Multi-Agent Integration Instructions

## Overview
This document provides technical instructions for integrating the Checkout Agent API as a tool in a multi-agent architecture. The API provides automated booking services for flights, hotels, and food delivery using AI-powered web automation.

## Base Configuration

**Base URL**: `https://checkout-agent-534113739138.europe-west1.run.app/api/v1`

**Content-Type**: `application/json`

**Authentication**: None required (currently public API)

## Available Endpoints

## Endpoint Selection Priority

### For Flight Bookings:
1. **PREFERRED: `/flights/book-direct`** - Use when you have a direct booking link from any provider (Booking.com, Ryanair, Expedia, etc.)
2. **FALLBACK: `/flights/book`** - Use only when you need to search for flights without a direct link

> **Why prioritize direct booking?** Direct booking links have significantly higher success rates, faster processing times, and fewer edge cases than search-based booking. The system can directly navigate to the specific flight selection page rather than performing complex search operations.

### 1. Flight Booking

#### Standard Flight Booking
**Endpoint**: `POST /flights/book`

**Use Case**: Book flights with search parameters when you don't have a direct booking link.

> **⚠️ Note**: Use the `/flights/book-direct` endpoint instead when you have a direct booking link from providers like Booking.com, Ryanair, Expedia, etc. Direct booking links are significantly more reliable and faster than search-based booking.

**Request Schema**:
```json
{
  "initial_url": "string (optional)",
  "departure": "string (required)",
  "destination": "string (required)", 
  "trip_type": "Round Trip | One Way (default: Round Trip)",
  "departure_date": "string (optional, format: YYYY-MM-DD)",
  "return_date": "string (optional, format: YYYY-MM-DD)",
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
    "country": "string (required)",
    "postal_code": "string (required)"
  }
}
```

#### Direct Flight Booking (Preferred Method)
**Endpoint**: `POST /flights/book-direct`

**Use Case**: Book flights using a direct booking link from providers like Booking.com, Ryanair, Expedia, etc.

> **✅ Recommended**: This is the preferred method for flight booking when you have a direct booking link. It's more reliable, faster, and has higher success rates than search-based booking.

**Request Schema**:
```json
{
  "direct_booking_link": "string (required)",
  "departure": "string (optional, overrides URL)",
  "destination": "string (optional, overrides URL)",
  "trip_type": "Round Trip | One Way (default: Round Trip)",
  "departure_date": "string (optional, overrides URL)",
  "return_date": "string (optional, overrides URL)",
  "budget": "string (optional)",
  "preferred_airlines": ["string"] (optional),
  "num_travelers": "integer (default: 1, overrides URL)",
  "traveler_info": {
    "first_name": "string (required)",
    "last_name": "string (required)",
    "email": "string (required)",
    "phone": "string (required)",
    "address": "string (required)",
    "city": "string (required)",
    "country": "string (required)",
    "postal_code": "string (required)"
  }
}
```

### 2. Hotel Booking

**Endpoint**: `POST /hotels/book`

**Request Schema**:
```json
{
  "initial_url": "string (optional)",
  "city": "string (required)",
  "location_preference": "string (optional)",
  "check_in_date": "string (optional, format: YYYY-MM-DD)",
  "check_out_date": "string (optional, format: YYYY-MM-DD)",
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

### 3. Food Delivery

**Endpoint**: `POST /food/book`

**Request Schema**:
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

## Response Format

All endpoints return the same structured response format:

```json
{
  "result": {
    "final_result": "string",
    "success": "boolean",
    "steps_completed": "integer",
    "execution_time_seconds": "float (optional)",
    "error_message": "string (optional)",
    "booking_details": "object (optional)"
  }
}
```

**Response Fields**:
- `final_result`: Human-readable description of the booking outcome
- `success`: Boolean indicating if the booking was successful
- `steps_completed`: Number of automation steps completed
- `execution_time_seconds`: How long the booking process took
- `error_message`: Error details if booking failed
- `booking_details`: Additional booking metadata (if available)

## Example Requests

### Flight Booking with Direct Link
```bash
curl -X POST "https://checkout-agent-534113739138.europe-west1.run.app/api/v1/flights/book-direct" \
  -H "Content-Type: application/json" \
  -d '{
    "direct_booking_link": "https://flights.booking.com/flights/LON.CITY-LYS.CITY?type=ONEWAY&adults=1&cabinClass=ECONOMY&from=LON.CITY&to=LYS.CITY&depart=2025-10-28",
    "departure": "London",
    "destination": "Lyon",
    "trip_type": "One Way",
    "departure_date": "2025-10-28",
    "num_travelers": 1,
    "traveler_info": {
      "first_name": "John",
      "last_name": "Doe",
      "email": "john.doe@example.com",
      "phone": "+44123456789",
      "address": "123 Main Street",
      "city": "London",
      "country": "United Kingdom",
      "postal_code": "SW1A 1AA"
    }
  }'
```

### Hotel Booking
```bash
curl -X POST "https://checkout-agent-534113739138.europe-west1.run.app/api/v1/hotels/book" \
  -H "Content-Type: application/json" \
  -d '{
    "city": "Paris",
    "location_preference": "Near Eiffel Tower",
    "check_in_date": "2025-08-01",
    "check_out_date": "2025-08-05",
    "budget": "200",
    "num_guests": 2,
    "room_type": "Double",
    "traveler_info": {
      "first_name": "Jane",
      "last_name": "Smith",
      "email": "jane.smith@example.com",
      "phone": "+33123456789",
      "address": "456 Rue de la Paix",
      "city": "Paris",
      "country": "France"
    }
  }'
```

### Food Delivery
```bash
curl -X POST "https://checkout-agent-534113739138.europe-west1.run.app/api/v1/food/book" \
  -H "Content-Type: application/json" \
  -d '{
    "cuisine": "Italian",
    "dishes": ["Pizza Margherita", "Tiramisu"],
    "delivery_address": "123 Oak Street, New York, NY 10001",
    "max_eta": "45 minutes",
    "budget": "50",
    "delivery_info": {
      "first_name": "Mike",
      "last_name": "Johnson",
      "email": "mike.johnson@example.com",
      "phone": "+1234567890",
      "address": "123 Oak Street",
      "city": "New York",
      "country": "USA"
    }
  }'
```

## Job Processing Model

### Important: Asynchronous Processing
- All booking requests trigger **asynchronous jobs** that run in the background
- The API responds immediately with a job initiation notification
- **No callbacks or webhook events are currently supported for success notifications**
- Jobs typically take 2-15 minutes to complete depending on complexity

### Expected Response Timeline
1. **Immediate**: API returns job initiation response
2. **Background**: Booking agent performs web automation
3. **Currently**: No automatic success notification (manual checking required)

## Error Handling

### HTTP Status Codes
- `200`: Job successfully initiated
- `422`: Validation error (invalid request schema)
- `500`: Internal server error (job failed to start)

### Error Response Format
```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common Error Scenarios
1. **Invalid traveler info**: Missing required fields like email, phone, address
2. **Invalid dates**: Malformed date formats or past dates
3. **Missing required fields**: departure/destination for flights, city for hotels, cuisine for food
4. **Server overload**: Too many concurrent bookings

## Integration Guidelines

### For Multi-Agent Systems
1. **Treat as fire-and-forget**: Send request and don't expect immediate completion
2. **Implement retry logic**: Handle 500 errors with exponential backoff
3. **Validate inputs**: Ensure all required fields are present before calling
4. **Monitor job status**: Currently requires manual monitoring (webhooks coming soon)

### Best Practices
1. **Always include complete traveler information** - incomplete info causes booking failures
2. **PRIORITIZE direct flight booking endpoint** - Use `/flights/book-direct` whenever you have a direct booking link from providers like Booking.com, Ryanair, Expedia, etc. This is significantly more reliable and faster than search-based booking via `/flights/book`
3. **Provide specific dates and preferences** - improves booking accuracy
4. **Set reasonable budgets** - helps guide the booking agent's choices
5. **Handle async nature** - Don't wait for synchronous responses

### Data Validation Requirements
- **Email**: Must be valid email format
- **Phone**: Include country code (e.g., +44, +1, +33)
- **Dates**: Use YYYY-MM-DD format
- **Postal codes**: Required for flight bookings
- **Addresses**: Be as specific as possible

## Limitations & Roadmap

### Current Limitations
- No real-time status updates during job execution
- No webhook notifications for job completion
- No job cancellation capability
- No booking modification/cancellation support

### Planned Features
- Webhook notifications for job completion
- Real-time job status endpoints
- Booking modification capabilities
- Enhanced error reporting with detailed failure reasons

## Health Check Endpoints

### Service Health
- `GET /health` - Detailed service health information
- `GET /` - Basic service status

These endpoints can be used to verify service availability before making booking requests.

## Support

For technical issues or questions about integration, monitor the service logs or implement local error handling as webhook notification support is not yet available. 