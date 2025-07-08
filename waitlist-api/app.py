from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, constr, conint, Field
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from groq import Groq

# Load environment variables
load_dotenv()

# Get MongoDB connection string from environment variables
mongo_connection_string = os.getenv("MONGO_CONNECTION_STRING")
if not mongo_connection_string:
    raise ValueError("MONGO_CONNECTION_STRING environment variable is not set")

# Initialize MongoDB client
client = MongoClient(mongo_connection_string)
db = client.Prosusware
collection = db.Waitlist

# Initialize Groq client
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    raise ValueError("GROQ_API_KEY environment variable is not set")
groq_client = Groq(api_key=groq_api_key)

app = FastAPI(title="Waitlist API")

# Allow all origins for CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SubscriptionSchema(BaseModel):
    email: EmailStr
    phone: str
    name: constr(min_length=1)
    paid: bool
    tier: str
    credits: conint(ge=0)
    subscription_start: str
    subscription_end: str

@app.post("/subscribe")
async def subscribe(subscription_data: SubscriptionSchema):
    # Check if email already exists
    if collection.find_one({"email": subscription_data.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Prepare data for insertion, allowing optional fields to be omitted
    subscription_data_dict = subscription_data.dict(exclude_unset=True)
    
    # Insert subscription data into database
    result = collection.insert_one(subscription_data_dict)
    
    if result.inserted_id:
        return {"status": "success", "message": "Email registered successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to register email")

@app.get("/")
async def root():
    return {"message": "Welcome to the Waitlist API"}

import stripe
from fastapi import Request

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# Pricing config (can be moved to a JSON or DB)
TIER_PRICING = {
    "6h": {"name": "6 Hour Express", "price_cents": 500},
    "24h": {"name": "24 Hour Fast Track", "price_cents": 1500},
    "7d": {"name": "7 Day Plan", "price_cents": 40000},
    "general": {"name": "General Access", "price_cents": 250},
}

@app.post("/create-checkout-session")
async def create_checkout_session(request: Request):
    body = await request.json()
    email = body.get("email") 
    tier = body.get("tier")

    if tier not in TIER_PRICING:
        raise HTTPException(status_code=400, detail="Invalid tier")

    price_info = TIER_PRICING[tier]

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="payment",
        customer_email=email,
        line_items=[{
            "price_data": {
                "currency": "eur",
                "product_data": {"name": price_info["name"]},
                "unit_amount": price_info["price_cents"],
            },
            "quantity": 1,
        }],
        success_url="https://yay.travel/confirmation?status=success",
        cancel_url="https://yay.travel/confirmation?status=cancel",
        metadata={"email": email, "tier": tier},
    )

    return {"url": session.url}

@app.post("/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        email = session["metadata"]["email"]
        tier = session["metadata"]["tier"]

        # Update user in MongoDB
        collection.update_one(
            {"email": email},
            {"$set": {"paid": True, "tier": tier}},
            upsert=True  # just in case
        )

    return {"status": "success"}

class TitleGenerationRequest(BaseModel):
    text: str = Field(..., description="Text to summarize for a thread title")

@app.post("/generate-title")
async def generate_title(request: TitleGenerationRequest):
    try:
        completion = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that generates concise, descriptive titles for chat threads based on the provided text. Keep titles short and informative."
                },
                {
                    "role": "user",
                    "content": f"Generate a short, concise title for a chat thread based on this text: {request.text}"
                }
            ],
            temperature=0.7,
            max_tokens=50,
            top_p=1,
            stream=False,
        )
        
        generated_title = completion.choices[0].message.content.strip()
        return {"title": generated_title}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Title generation failed: {str(e)}")