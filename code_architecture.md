# Humming Bird Backend Architecture
<img width="1159" alt="Screenshot 2025-04-13 at 10 07 59 AM" src="https://github.com/user-attachments/assets/fdf30a44-ecbd-4538-8dae-29fe36dda8c3" />

## Overview
Humming Bird Backend is a FastAPI application that provides AI-powered product recommendations based on user conversations. The system uses multiple AI services including OpenAI and Portia to generate tailored product suggestions.

## Core Components

### 1. API Layer
- **main.py**: Entry point for the FastAPI application
  - Sets up CORS middleware, routes, and WebSocket connections
  - Provides health check endpoint

- **routes/route.py**: API route definitions
  - `/api/v1/clarify`: Generates clarifying questions for user input
  - `/api/v1/conversation/end`: Handles session termination
  - `/api/v1/products/{session_id}`: Retrieves product recommendations

### 2. Services Layer
- **portiai_service.py**: Core orchestration service
  - Initializes AI tools and services
  - Loads and runs generation plans against user conversations
  - Integrates with LogoSearchService for enhancing product results

- **logo_search.py**: Logo retrieval service
  - Searches for product logos using OpenAI
  - Implements caching for efficient retrieval
  - Validates image URLs and extracts from text responses

- **fetchers.py**: Conversation management
  - Handles storage of user conversations
  - Generates clarifying questions
  - Prepares data for product generation

### 3. AI Tools
- **custom_tool.py**: Custom tools for Portia framework
  - `LLMstructureTool`: Creates structured product data
  - `LLMlistTool`: Generates list-based responses
  - `SearchTool`: Performs internet searches via Tavily API

### 4. Plan Definitions
- **generation_plan.json**: Defines execution plan for product generation
  - Three-step process: identify stages, find tools, structure output

### 5. Data Storage
- **logo_cache.json**: Local cache for logo URLs
  - Maps product names to their logo URLs
  - Prevents redundant API calls

### 6. Utilities
- **logging_config.py**: Centralized logging configuration
  - File and console log handlers
  - Log rotation for long-running deployments

## Data Flow
1. User input arrives via API endpoint
2. System generates clarifying questions until sufficient information is gathered
3. Conversation is processed through Portia AI Service
4. The service executes a generation plan to identify product stages and tools
5. Products are enhanced with logo URLs from LogoSearchService
6. Final structured output is returned to the client

## Key Technologies
- FastAPI for API endpoints and WebSockets
- OpenAI API for language processing and web searches
- Portia framework for multi-step AI task execution
- Python async/await for non-blocking operations

## External Dependencies
- Tavily for web search functionality
- OpenAI API for LLM capabilities
- WebSockets for real-time logging and communication

This architecture enables the system to have a conversation with users, understand their needs, and generate relevant product recommendations with minimal latency.
