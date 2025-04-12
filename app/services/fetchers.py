import logging
from typing import Optional, List
from app.models.products import ProductSuggestion

logger = logging.getLogger(__name__)

# Store conversations in memory for now
conversations = {}


async def call_deepresearch(user_input: str, session_id: str) -> Optional[str]:
    try:
        # Simulated async call to research engine
        # Replace with actual model call
        logger.info(
            f"Calling deep research for session {session_id} with input: {user_input}"
        )
        return "What specific features are you looking for in this product?"
    except Exception as e:
        logger.error(f"Error in deep research call: {str(e)}")
        raise


async def fetch_product_suggestions(session_id: str) -> List[ProductSuggestion]:
    try:
        # Replace with actual logic
        logger.info(f"Fetching product suggestions for session {session_id}")
        return [
            ProductSuggestion(
                id="1",
                name="Sample Product",
                description="A great product",
                website_url="https://example.com",
                image_url="https://example.com/image.jpg",
            )
        ]
    except Exception as e:
        logger.error(f"Error fetching product suggestions: {str(e)}")
        raise


def store_conversation(
    session_id: str, user_input: str, agent_response: Optional[str] = None
):
    conversations.setdefault(session_id, []).append({"user": user_input})
    if agent_response:
        conversations[session_id].append({"agent": agent_response})
    logger.info(f"Stored conversation for session {session_id}")
