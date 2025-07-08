# Waitlist API

A simple FastAPI application that collects email addresses for a waitlist and stores them in MongoDB. As well as managing anciliary services for onboarding users

## Setup

1. Create a `.env` file in the root directory with your MongoDB connection string:
   ```
   MONGO_CONNECTION_STRING=mongodb://localhost:27017/
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   uvicorn app:app --reload
   ```

## API Endpoints

- `GET /`: Welcome message
- `POST /subscribe`: Register an email address
  - Request body: `{"email": "user@example.com", "phone": "1234567890", "name": "John Doe", "paid": false, "tier": "6h", "credits": 0, "subscription_start": "2023-01-01", "subscription_end": "2023-12-31"}`
- `POST /create-checkout-session`: Create a checkout session for payment
  - Request body: `{"email": "user@example.com", "tier": "6h"}`
- `POST /webhook`: Stripe webhook for payment confirmation
- `POST /generate-title`: Generate a title for a chat thread
  - Request body: `{"text": "Some text to summarize"}`

## Documentation

Designed to be deployed on cloud run
