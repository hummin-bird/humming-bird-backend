from fastapi import APIRouter, Request, HTTPException, Depends
from typing import Dict, Any
from app.services.deep_research import deep_research_service
from app.core.config import settings
import hmac
import hashlib
import json

router = APIRouter()

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

@router.post("/elevenlabs-webhook")
async def elevenlabs_webhook(webhook_data: Dict[str, Any] = Depends(verify_webhook_signature)):
    """
    Endpoint to receive webhooks from ElevenLabs
    """
    try:
        # Process the webhook data using the Deep Research service
        result = await deep_research_service.process_audio_data(webhook_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 