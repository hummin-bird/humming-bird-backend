from fastapi import APIRouter, Request, HTTPException, Body
from pydantic import BaseModel
from typing import Optional, Dict, Any
import hmac
import hashlib
import json
from app.core.config import settings

router = APIRouter()

class ElevenLabsRequest(BaseModel):
    user_input: str
    session_id: str


class ClarifyingResponse(BaseModel):
    clarifying_question: Optional[str]


class ProductSuggestion(BaseModel):
    id: str
    name: str
    description: str
    website_url: Optional[str]
    image_url: Optional[str]


# Store conversations in memory for now
conversations = {}

async def verify_webhook_signature(request: Request) -> Dict[str, Any]:
    """
    Verify the webhook signature from ElevenLabs
    """
    try:
        body = await request.body()
        signature = request.headers.get("X-ElevenLabs-Signature")
        
        if not signature or not settings.ELEVENLABS_WEBHOOK_SECRET:
            raise HTTPException(status_code=401, detail="Missing signature or webhook secret")
        
        # Verify the signature
        expected_signature = hmac.new(
            settings.ELEVENLABS_WEBHOOK_SECRET.encode(),
            body,
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(signature, expected_signature):
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        return json.loads(body)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/clarify")
async def clarify(request: Request):
    # Verify webhook signature and get request body
    body = await verify_webhook_signature(request)
    request_data = ElevenLabsRequest(**body)
    
    session_id = request_data.session_id
    user_input = request_data.user_input

    # Store or append to session
    conversations.setdefault(session_id, []).append({"user": user_input})

    clarifying_question = await call_deepresearch(user_input, session_id)

    if clarifying_question:
        conversations[session_id].append({"agent": clarifying_question})
        return {"clarifying_question": clarifying_question}
    else:
        # No more questions, agent is done
        return {"clarifying_question": None}

@router.post("/conversation/end")
async def end_session(request: Request):
    # Verify webhook signature
    await verify_webhook_signature(request)
    
    # Could trigger any cleanup, caching, etc.
    print(f"Session ended.")
    return {"status": "ended"}

@router.get("/products/{session_id}")
async def get_products(session_id: str, request: Request):
    # Verify webhook signature
    await verify_webhook_signature(request)
    
    # Final call to research model for product listing
    products = await fetch_product_suggestions(session_id)
    return {"products": products}

async def call_deepresearch(user_input: str, session_id: str) -> Optional[str]:
    # Simulated async call to research engine
    # Replace with actual model call
    return "What specific features are you looking for in this product?"

async def fetch_product_suggestions(session_id: str):
    # Replace with actual logic
    return [
        {
            "id": "1",
            "name": "Sample Product",
            "description": "A great product",
            "website_url": "https://example.com",
            "image_url": "https://example.com/image.jpg"
        }
    ]
