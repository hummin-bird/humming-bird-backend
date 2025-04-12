import logging
from typing import Optional, List, Dict, Any
import random

logger = logging.getLogger(__name__)

# Store conversations in memory for now
conversations = {}

# Question categories and their questions
QUESTION_CATEGORIES = {
    "target_audience": [
        "Who are you hoping to delight with this product? Are they young professionals, busy parents, creative students, or someone else entirely?",
        "What's something your ideal user struggles with that your product might help with?",
        "If you could picture your perfect customer, what are three words you'd use to describe them?"
    ],
    "product_purpose": [
        "In one sentence, what problem is your product trying to solve for people?",
        "What's the biggest impact you'd love your product to have on its users' lives?",
        "Is this product meant to inform, entertain, simplify, connect, or something else entirely?"
    ],
    "features": [
        "If you had a magic wand, what's the one must-have feature your product absolutely needs?",
        "Which three core features would make your product both useful and delightful for your audience?",
        "Are there any fun, quirky, or unique functionalities you'd love to sneak in, even just for extra charm?"
    ],
    "budget": [
        "Do you have a set budget in mind for building this, or are you exploring what's possible first?",
        "What kind of resources or team members do you have on hand — designers, developers, marketers?",
        "Would you prefer to build this lean and scrappy to start, or invest in a polished, full-featured version right away?"
    ],
    "market_research": [
        "Have you seen any similar products out there? What do you love or wish was different about them?",
        "Why do you believe now is the perfect time for this product to exist?",
        "What makes your idea stand out from the crowd? What's the spark that makes it special?"
    ]
}

# Track which questions have been asked for each session
session_questions = {}

async def call_deepresearch(user_input: str, session_id: str) -> Optional[str]:
    try:
        logger.info(f"Calling deep research for session {session_id} with input: {user_input}")
        
        # Initialize session tracking if it doesn't exist
        if session_id not in session_questions:
            session_questions[session_id] = {
                category: [] for category in QUESTION_CATEGORIES.keys()
            }
        
        # Get available categories (those that haven't had all questions asked)
        available_categories = [
            category for category, questions in QUESTION_CATEGORIES.items()
            if len(session_questions[session_id][category]) < len(questions)
        ]
        
        if not available_categories:
            logger.info(f"No more questions available for session {session_id}")
            return None
        
        # Randomly select a category
        selected_category = random.choice(available_categories)
        
        # Get available questions for this category
        asked_questions = session_questions[session_id][selected_category]
        available_questions = [
            q for q in QUESTION_CATEGORIES[selected_category]
            if q not in asked_questions
        ]
        
        # Select a random question from available ones
        selected_question = random.choice(available_questions)
        
        # Mark this question as asked
        session_questions[session_id][selected_category].append(selected_question)
        
        logger.info(f"Selected question from category '{selected_category}' for session {session_id}")
        return selected_question
        
    except Exception as e:
        logger.error(f"Error in deep research call: {str(e)}")
        raise

async def fetch_product_suggestions(session_id: str) -> List[Dict[str, Any]]:
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

def store_conversation(session_id: str, user_input: str, clarifying_question: Optional[str] = None) -> None:
    """
    Store conversation data for a session
    """
    try:
        if session_id not in conversations:
            conversations[session_id] = []
        
        conversation_entry = {
            "user_input": user_input,
            "clarifying_question": clarifying_question
        }
        
        conversations[session_id].append(conversation_entry)
        logger.info(f"Stored conversation for session {session_id}")
    except Exception as e:
        logger.error(f"Error storing conversation: {str(e)}")
        raise
