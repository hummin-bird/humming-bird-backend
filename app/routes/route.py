from fastapi import APIRouter, Request, HTTPException
from pydantic import ValidationError
import logging
from app.models.elevenlabs import ElevenLabsRequest
from app.utils.webhook import verify_webhook_signature
from app.services.fetchers import (
    call_deepresearch,
    fetch_product_suggestions,
    store_conversation,
)

logger = logging.getLogger(__name__)

router = APIRouter()


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

        # Store conversation
        store_conversation(session_id, user_input)

        try:
            clarifying_question = await call_deepresearch(user_input, session_id)
        except Exception as e:
            logger.error(f"Error in deep research: {str(e)}")
            raise HTTPException(status_code=500, detail="Error processing request")

        if clarifying_question:
            store_conversation(session_id, user_input, clarifying_question)
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
