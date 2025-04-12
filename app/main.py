from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from app.routes.route import router
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Humming Bird Backend",
    description="Backend API for Humming Bird application",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router, prefix="/api/v1")

# Add a global WebSocket endpoint
@app.websocket("/ws/logs/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    from app.utils.websocket_manager import websocket_manager
    await websocket_manager.connect(websocket, session_id)
    try:
        while True:
            # Keep the connection alive
            data = await websocket.receive_text()
            # You can handle any client messages here if needed
    except Exception as e:
        logger.error(f"WebSocket error for session {session_id}: {str(e)}")
    finally:
        websocket_manager.disconnect(websocket, session_id)

@app.get("/")
async def root():
    return {"message": "Welcome to Humming Bird Backend API"}
