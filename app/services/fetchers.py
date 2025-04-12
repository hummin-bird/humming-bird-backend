import logging
from typing import Optional, List, Dict, Any
import random
import asyncio
import json
from datetime import datetime

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
        logger.info(f"Starting deep research for session {session_id}")
        logger.debug(f"User input: {user_input[:100]}...")

        async with session_lock:
            # Initialize session tracking if it doesn't exist
            if session_id not in session_questions:
                session_questions[session_id] = {
                    category: [] for category in QUESTION_CATEGORIES.keys()
                }
                logger.debug(f"Initialized new session questions for {session_id}")

            # Get available categories (those that haven't had any questions asked)
            available_categories = [
                category
                for category in QUESTION_CATEGORIES.keys()
                if not session_questions[session_id][category]
            ]
            logger.debug(
                f"Available categories for {session_id}: {available_categories}"
            )

            if not available_categories:
                logger.info(f"No more questions available for session {session_id}")
                return "All needed clarifications have been gathered, please end the conversation"

            # Randomly select a category
            selected_category = random.choice(available_categories)
            logger.debug(f"Selected category: {selected_category}")

            # Get all questions for this category
            available_questions = QUESTION_CATEGORIES[selected_category]

            # Select a random question from available ones
            selected_question = random.choice(available_questions)
            logger.debug(f"Selected question: {selected_question[:100]}...")

            # Mark this question as asked
            session_questions[session_id][selected_category].append(selected_question)
            logger.info(f"Question marked as asked for session {session_id}")

            return selected_question

    except Exception as e:
        logger.error(f"Error in deep research call for session {session_id}: {str(e)}")
        raise


async def fetch_product_suggestions(session_id: str) -> List[Dict[str, Any]]:
    try:
        logger.info(f"Starting product suggestions fetch for session {session_id}")

        # Get the conversation history for this session
        if session_id not in conversations or not conversations[session_id]:
            logger.warning(f"No conversation history found for session {session_id}")
            return [
                {
                    "id": "default",
                    "name": "No products available",
                    "description": "Please complete the conversation to get personalized product suggestions",
                    "website_url": "https://example.com",
                    "image_url": "https://example.com/image.jpg",
                }
            ]

        # Create a text data string from the conversation history
        try:
            text_data = "\n".join(
                [
                    f"User: {entry['user_input']}\nAssistant: {entry['clarifying_question']}"
                    for entry in conversations[session_id]
                    if entry["user_input"] and entry["clarifying_question"]
                ]
            )

            if not text_data:
                logger.warning(f"Empty conversation history for session {session_id}")
                return [
                    {
                        "id": "default",
                        "name": "No products available",
                        "description": "Please complete the conversation to get personalized product suggestions",
                        "website_url": "https://example.com",
                        "image_url": "https://example.com/image.jpg",
                    }
                ]

            logger.debug(
                f"Created text data from conversation history for session {session_id}"
            )

            # Initialize PortiaAI service
            portia_service = PortiaAIService()
            logger.debug("Initialized PortiaAI service")

            try:
                # Generate tools and get products
                await portia_service.generate_tools(text_data)
                logger.info(f"Successfully generated tools for session {session_id}")

                # Get products for each step (assuming 3 steps as shown in the example)
                products = []
                for step in range(3):
                    try:
                        step_products = portia_service.get_products(step)
                        if step_products:  # Only extend if we got products
                            products.extend(step_products)
                            logger.info(
                                f"Retrieved {len(step_products)} products for step {step} in session {session_id}"
                            )
                    except Exception as e:
                        logger.error(
                            f"Error getting products for step {step} in session {session_id}: {str(e)}"
                        )
                        continue

                if not products:  # If no products were retrieved
                    logger.warning(f"No products retrieved for session {session_id}")
                    return [
                        {
                            "id": "default",
                            "name": "No products available",
                            "description": "Please complete the conversation to get personalized product suggestions",
                            "website_url": "https://example.com",
                            "image_url": "https://example.com/image.jpg",
                        }
                    ]

                logger.info(
                    f"Successfully retrieved {len(products)} total products for session {session_id}"
                )
                return products

            except Exception as e:
                logger.error(
                    f"Error in PortiaAI service for session {session_id}: {str(e)}"
                )
                return [
                    {
                        "id": "default",
                        "name": "Error retrieving products",
                        "description": "We encountered an error while retrieving product suggestions. Please try again later.",
                        "website_url": "https://example.com",
                        "image_url": "https://example.com/image.jpg",
                    }
                ]

        except Exception as e:
            logger.error(
                f"Error processing conversation history for session {session_id}: {str(e)}"
            )
            return [
                {
                    "id": "default",
                    "name": "Error processing request",
                    "description": "We encountered an error while processing your request. Please try again later.",
                    "website_url": "https://example.com",
                    "image_url": "https://example.com/image.jpg",
                }
            ]

    except Exception as e:
        logger.error(
            f"Error fetching product suggestions for session {session_id}: {str(e)}"
        )
        return [
            {
                "id": "default",
                "name": "Error",
                "description": "We encountered an error. Please try again later.",
                "website_url": "https://example.com",
                "image_url": "https://example.com/image.jpg",
            }
        ]


def store_conversation(
    session_id: str, user_input: str, clarifying_question: Optional[str] = None
) -> None:
    """
    Store conversation data for a session
    """
    try:
        logger.info(f"Storing conversation for session {session_id}")
        logger.debug(f"User input: {user_input[:100]}...")
        logger.debug(
            f"Clarifying question: {clarifying_question[:100] if clarifying_question else 'None'}"
        )

        if session_id not in conversations:
            conversations[session_id] = []
            logger.debug(
                f"Initialized new conversation history for session {session_id}"
            )

        conversation_entry = {
            "user_input": user_input,
            "clarifying_question": clarifying_question,
            "timestamp": datetime.now().isoformat(),
        }

        conversations[session_id].append(conversation_entry)
        logger.info(f"Successfully stored conversation entry for session {session_id}")

        # Log the current state of the conversation
        logger.debug(
            f"Current conversation length for session {session_id}: {len(conversations[session_id])}"
        )

    except Exception as e:
        logger.error(f"Error storing conversation for session {session_id}: {str(e)}")
        raise
