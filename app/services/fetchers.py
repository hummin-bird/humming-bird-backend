import logging
from typing import Optional, List, Dict, Any
import random
import asyncio

logger = logging.getLogger(__name__)

# Store conversations in memory for now
conversations = {}

# Question categories and their questions
QUESTION_CATEGORIES = {
    "target_audience": [
        "Who are you hoping to delight with this product? Are they young professionals, busy parents, creative students, or someone else entirely?",
        "What's something your ideal user struggles with that your product might help with?",
        "If you could picture your perfect customer, what are three words you'd use to describe them?",
    ],
    "product_purpose": [
        "In one sentence, what problem is your product trying to solve for people?",
        "What's the biggest impact you'd love your product to have on its users' lives?",
    ],
    "features": [
        "If you had a magic wand, what's the one must-have feature your product absolutely needs?",
        "Which three core features would make your product both useful and delightful for your audience?",
        "Are there any fun, quirky, or unique functionalities you'd love to sneak in, even just for extra charm?",
    ],
    "budget": [
        "Do you have a set budget in mind for building this, or are you exploring what's possible first?",
        "Would you prefer to build this lean and scrappy to start, or invest in a polished, full-featured version right away?",
    ],
    "market_research": [
        "Have you seen any similar products out there? What do you love or wish was different about them?",
        "Why do you believe now is the perfect time for this product to exist?",
        "What makes your idea stand out from the crowd? What's the spark that makes it special?",
    ],
}

# Track which questions have been asked for each session
session_questions = {}
# Lock for synchronizing access to session_questions
session_lock = asyncio.Lock()


async def call_deepresearch(user_input: str, session_id: str) -> Optional[str]:
    try:
        logger.info(
            f"Calling deep research for session {session_id} with input: {user_input}"
        )

        async with session_lock:
            # Initialize session tracking if it doesn't exist
            if session_id not in session_questions:
                session_questions[session_id] = {
                    category: [] for category in QUESTION_CATEGORIES.keys()
                }

            # Get available categories (those that haven't had any questions asked)
            available_categories = [
                category
                for category in QUESTION_CATEGORIES.keys()
                if not session_questions[session_id][category]
            ]

            if not available_categories:
                logger.info(f"No more questions available for session {session_id}")
                return "All needed clarifications have been gathered, please end the conversation"

            # Randomly select a category
            selected_category = random.choice(available_categories)

            # Get all questions for this category
            available_questions = QUESTION_CATEGORIES[selected_category]

            # Select a random question from available ones
            selected_question = random.choice(available_questions)

            # Mark this question as asked
            session_questions[session_id][selected_category].append(selected_question)

            logger.info(
                f"Selected question from category '{selected_category}' for session {session_id}"
            )
            return selected_question

    except Exception as e:
        logger.error(f"Error in deep research call: {str(e)}")
        raise


async def fetch_product_suggestions(session_id: str) -> List[Dict[str, Any]]:
    try:
        # Replace with actual logic
        logger.info(f"Fetching product suggestions for session {session_id}")

        # Get the conversation history for this session
        if session_id not in conversations:
            logger.warning(f"No conversation history found for session {session_id}")
            return []

        # Create a text data string from the conversation history
        text_data = "\n".join(
            [
                f"User: {entry['user_input']}\nAssistant: {entry['clarifying_question']}"
                for entry in conversations[session_id]
            ]
        )

        # Initialize PortiaAI service
        portia_service = PortiaAIService()

        try:
            # Generate tools and get products
            await portia_service.generate_tools(text_data)
            logger.info(f"Successfully generated tools for session {session_id}")

            # Get products for each step (assuming 3 steps as shown in the example)
            products = []
            for step in range(3):
                try:
                    step_products = portia_service.get_products(step)
                    products.extend(step_products)
                    logger.info(
                        f"Retrieved {len(step_products)} products for step {step} in session {session_id}"
                    )
                except Exception as e:
                    logger.error(
                        f"Error getting products for step {step} in session {session_id}: {str(e)}"
                    )
                    continue

            logger.info(
                f"Successfully retrieved {len(products)} total products for session {session_id}"
            )
            return products

        except Exception as e:
            logger.error(
                f"Error in PortiaAI service for session {session_id}: {str(e)}"
            )
            raise

    except Exception as e:
        logger.error(
            f"Error fetching product suggestions for session {session_id}: {str(e)}"
        )
        raise


def store_conversation(
    session_id: str, user_input: str, clarifying_question: Optional[str] = None
) -> None:
    """
    Store conversation data for a session
    """
    try:
        if session_id not in conversations:
            conversations[session_id] = []

        conversation_entry = {
            "user_input": user_input,
            "clarifying_question": clarifying_question,
        }

        conversations[session_id].append(conversation_entry)
        logger.info(f"Stored conversation for session {session_id}")
    except Exception as e:
        logger.error(f"Error storing conversation: {str(e)}")
        raise
