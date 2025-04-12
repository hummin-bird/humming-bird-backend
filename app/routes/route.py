from fastapi import APIRouter, Request, HTTPException, Body
from pydantic import BaseModel, ValidationError
from typing import Optional, Dict, Any
import hmac
import hashlib
import json
import logging
from app.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        
        # Log the incoming request
        logger.info(f"Incoming request: {request.method} {request.url}")
        logger.info(f"Headers: {dict(request.headers)}")
        logger.info(f"Body: {body.decode()}")
        
        if not signature or not settings.ELEVENLABS_WEBHOOK_SECRET:
            logger.error("Missing signature or webhook secret")
            raise HTTPException(status_code=401, detail="Missing signature or webhook secret")
        
        # Verify the signature
        expected_signature = hmac.new(
            settings.ELEVENLABS_WEBHOOK_SECRET.encode(),
            body,
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(signature, expected_signature):
            logger.error(f"Invalid signature. Expected: {expected_signature}, Got: {signature}")
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        return json.loads(body)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in request body: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid JSON in request body")
    except Exception as e:
        logger.error(f"Error verifying webhook signature: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/clarify")
async def clarify(request: Request):
    try:
        # Verify webhook signature and get request body
        body = await verify_webhook_signature(request)
        
        try:
            request_data = ElevenLabsRequest(**body)
        except ValidationError as e:
            logger.error(f"Invalid request data: {str(e)}")
            logger.error(f"Request body: {body}")
            raise HTTPException(status_code=422, detail=str(e))
        
        session_id = request_data.session_id
        user_input = request_data.user_input

        # Store or append to session
        conversations.setdefault(session_id, []).append({"user": user_input})
        logger.info(f"Stored conversation for session {session_id}")

        try:
            clarifying_question = await call_deepresearch(user_input, session_id)
        except Exception as e:
            logger.error(f"Error in deep research: {str(e)}")
            raise HTTPException(status_code=500, detail="Error processing request")

        if clarifying_question:
            conversations[session_id].append({"agent": clarifying_question})
            logger.info(f"Added clarifying question for session {session_id}")
            return {"clarifying_question": clarifying_question}
        else:
            logger.info(f"No more questions needed for session {session_id}")
            return {"clarifying_question": None}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in clarify endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/conversation/end")
async def end_session(request: Request):
    try:
        # Verify webhook signature
        body = await verify_webhook_signature(request)
        
        try:
            request_data = ElevenLabsRequest(**body)
            session_id = request_data.session_id
        except ValidationError as e:
            logger.error(f"Invalid request data: {str(e)}")
            logger.error(f"Request body: {body}")
            raise HTTPException(status_code=422, detail=str(e))
        
        # Could trigger any cleanup, caching, etc.
        logger.info(f"Session {session_id} ended.")
        return {"status": "ended"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in end_session endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/products/{session_id}")
async def get_products(session_id: str, request: Request):
    try:
        # Verify webhook signature
        await verify_webhook_signature(request)
        
        try:
            # Final call to research model for product listing
            products = await fetch_product_suggestions(session_id)
            logger.info(f"Retrieved {len(products)} products for session {session_id}")
            return {"products": products}
        except Exception as e:
            logger.error(f"Error fetching products: {str(e)}")
            raise HTTPException(status_code=500, detail="Error fetching products")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_products endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def call_deepresearch(user_input: str, session_id: str) -> Optional[str]:
    try:
        # Simulated async call to research engine
        # Replace with actual model call
        logger.info(f"Calling deep research for session {session_id} with input: {user_input}")
        return "What specific features are you looking for in this product?"
    except Exception as e:
        logger.error(f"Error in deep research call: {str(e)}")
        raise

async def fetch_product_suggestions(session_id: str):
    try:
        # Replace with actual logic
        logger.info(f"Fetching product suggestions for session {session_id}")
        return [
            {
                "id": "1",
                "name": "Sample Product",
                "description": "A great product",
                "website_url": "https://example.com",
                "image_url": "https://example.com/image.jpg"
            }
        ]
    except Exception as e:
        logger.error(f"Error fetching product suggestions: {str(e)}")
        raise
