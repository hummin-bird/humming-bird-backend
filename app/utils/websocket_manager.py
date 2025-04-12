from typing import Set, Dict
import json
import logging
from fastapi import WebSocket
from datetime import datetime

logger = logging.getLogger(__name__)

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.log_handlers: Dict[str, logging.Handler] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = set()
        self.active_connections[session_id].add(websocket)
        
        # Create a custom log handler for this session if it doesn't exist
        if session_id not in self.log_handlers:
            handler = WebSocketLogHandler(self, session_id)
            self.log_handlers[session_id] = handler
            logging.getLogger().addHandler(handler)
        
        logger.info(f"WebSocket connected for session {session_id}")

    def disconnect(self, websocket: WebSocket, session_id: str):
        if session_id in self.active_connections:
            self.active_connections[session_id].remove(websocket)
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]
                # Remove the log handler if no more connections for this session
                if session_id in self.log_handlers:
                    logging.getLogger().removeHandler(self.log_handlers[session_id])
                    del self.log_handlers[session_id]
        logger.info(f"WebSocket disconnected for session {session_id}")

    async def broadcast_log(self, session_id: str, message: str, level: str):
        if session_id in self.active_connections:
            log_data = {
                "timestamp": datetime.now().isoformat(),
                "level": level,
                "message": message
            }
            for connection in self.active_connections[session_id]:
                try:
                    await connection.send_json(log_data)
                except Exception as e:
                    logger.error(f"Error sending log to WebSocket: {str(e)}")
                    self.disconnect(connection, session_id)

class WebSocketLogHandler(logging.Handler):
    def __init__(self, manager: WebSocketManager, session_id: str):
        super().__init__()
        self.manager = manager
        self.session_id = session_id

    def emit(self, record):
        try:
            msg = self.format(record)
            # Use asyncio to run the broadcast in the event loop
            import asyncio
            asyncio.create_task(self.manager.broadcast_log(self.session_id, msg, record.levelname))
        except Exception as e:
            logger.error(f"Error emitting log to WebSocket: {str(e)}")

# Create a global instance of the WebSocket manager
websocket_manager = WebSocketManager() 