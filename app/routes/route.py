from fastapi import APIRouter, Request, HTTPException
from pydantic import ValidationError
import logging
from app.models.elevenlabs import ElevenLabsRequest
from app.utils.webhook import verify_webhook_signature
from app.services.fetchers import (
    call_deepresearch,
    fetch_product_suggestions,
    store_conversation,
    conversations,
)
from app.utils.websocket_manager import websocket_manager
from app.services.portiai_service import PortiaAIService

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
            # Create a session-specific PortiaAIService
            service = PortiaAIService(session_id=session_id)
            
            # Get the conversation history for this session
            if session_id not in conversations or not conversations[session_id]:
                logger.warning(f"No conversation history found for session {session_id}")
                return {
                    "products": [
                        {
                            "id": "default",
                            "name": "No products available",
                            "description": "Please complete the conversation to get personalized product suggestions",
                            "website_url": "https://example.com",
                            "image_url": "https://example.com/image.jpg",
                        }
                    ]
                }

            # Create a text data string from the conversation history
            text_data = ""
            for entry in conversations[session_id]:
                if entry["user_input"]:
                    text_data += f"User: {entry['user_input']}\n"
                if entry["clarifying_question"]:
                    text_data += f"Assistant: {entry['clarifying_question']}\n"

            # Generate products using PortiaAIService
            products = await service.generate_tools(text_data)
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
