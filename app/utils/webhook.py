from fastapi import Request, HTTPException
from typing import Dict, Any
import hmac
import hashlib
import json
import logging
from app.config import settings

logger = logging.getLogger(__name__)


async def verify_webhook_signature(request: Request) -> Dict[str, Any]:
    """
    Verify the webhook signature from ElevenLabs if present
    """
    try:
        # For GET requests, we don't expect a body
        if request.method == "GET":
            logger.info("GET request, skipping body verification")
            return {}

        body = await request.body()
        signature = request.headers.get("X-ElevenLabs-Signature")

        # Log the incoming request
        logger.info(f"Incoming request: {request.method} {request.url}")
        logger.info(f"Headers: {dict(request.headers)}")
        if body:
            logger.info(f"Body: {body.decode()}")

        # If no signature is present, just return the parsed body
        if not signature:
            logger.info("No signature present, skipping verification")
            if not body:
                return {}
            return json.loads(body)

        # If signature is present but no secret is configured
        if not settings.ELEVENLABS_WEBHOOK_SECRET:
            logger.error("Webhook secret not configured but signature present")
            raise HTTPException(status_code=401, detail="Webhook secret not configured")

        # Verify the signature
        expected_signature = hmac.new(
            settings.ELEVENLABS_WEBHOOK_SECRET.encode(), body, hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(signature, expected_signature):
            logger.error(
                f"Invalid signature. Expected: {expected_signature}, Got: {signature}"
            )
            raise HTTPException(status_code=401, detail="Invalid signature")

        return json.loads(body)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in request body: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid JSON in request body")
    except Exception as e:
        logger.error(f"Error verifying webhook signature: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
