from typing import Set, Dict
import json
import logging
from fastapi import WebSocket
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.log_handlers: Dict[str, logging.Handler] = {}
        self.ping_interval = 30  # seconds
        self.ping_timeout = 10  # seconds

    async def connect(self, websocket: WebSocket, session_id: str):
        if session_id not in self.active_connections:
            self.active_connections[session_id] = set()
        self.active_connections[session_id].add(websocket)
        
        # Create a custom log handler for this session if it doesn't exist
        if session_id not in self.log_handlers:
            handler = WebSocketLogHandler(self, session_id)
            self.log_handlers[session_id] = handler
            logging.getLogger().addHandler(handler)
        
        logger.info(f"WebSocket connected for session {session_id}")
        
        # Start ping task
        asyncio.create_task(self._ping_task(websocket, session_id))

    async def _ping_task(self, websocket: WebSocket, session_id: str):
        try:
            while True:
                await asyncio.sleep(self.ping_interval)
                try:
                    await websocket.send_json({"type": "ping"})
                    # Wait for pong response
                    try:
                        data = await asyncio.wait_for(websocket.receive_text(), timeout=self.ping_timeout)
                        if data != "pong":
                            logger.warning(f"Invalid response to ping from session {session_id}")
                            break
                    except asyncio.TimeoutError:
                        logger.warning(f"Ping timeout for session {session_id}")
                        break
                except Exception as e:
                    logger.error(f"Error sending ping to session {session_id}: {str(e)}")
                    break
        except Exception as e:
            logger.error(f"Error in ping task for session {session_id}: {str(e)}")
        finally:
            self.disconnect(websocket, session_id)

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
            asyncio.create_task(self.manager.broadcast_log(self.session_id, msg, record.levelname))
        except Exception as e:
            logger.error(f"Error emitting log to WebSocket: {str(e)}")

# Create a global instance of the WebSocket manager
websocket_manager = WebSocketManager() 