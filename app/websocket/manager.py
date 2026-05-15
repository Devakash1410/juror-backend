"""
WebSocket connection manager for real-time updates.
"""
from fastapi import WebSocket
from typing import Set, Dict
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ConnectionManager:
    """Manage WebSocket connections."""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.analysis_subscriptions: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket):
        """Accept a new connection."""
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"WebSocket connected. Total: {len(self.active_connections)}")
    
    async def disconnect(self, websocket: WebSocket):
        """Remove a connection."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")
        
        # Remove from analysis subscriptions
        for analysis_id in list(self.analysis_subscriptions.keys()):
            if websocket in self.analysis_subscriptions[analysis_id]:
                self.analysis_subscriptions[analysis_id].remove(websocket)
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connections."""
        if not self.active_connections:
            return
        
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting: {e}")
    
    async def send_personal(self, websocket: WebSocket, message: dict):
        """Send message to specific connection."""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
    
    async def subscribe_to_analysis(self, analysis_id: str, websocket: WebSocket):
        """Subscribe to analysis updates."""
        if analysis_id not in self.analysis_subscriptions:
            self.analysis_subscriptions[analysis_id] = set()
        self.analysis_subscriptions[analysis_id].add(websocket)
        logger.info(f"Subscribed to analysis {analysis_id}")
    
    async def unsubscribe_from_analysis(self, analysis_id: str, websocket: WebSocket):
        """Unsubscribe from analysis updates."""
        if analysis_id in self.analysis_subscriptions:
            self.analysis_subscriptions[analysis_id].discard(websocket)
    
    async def broadcast_to_analysis(self, analysis_id: str, message: dict):
        """Broadcast to specific analysis subscribers."""
        if analysis_id in self.analysis_subscriptions:
            for connection in self.analysis_subscriptions[analysis_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error broadcasting to analysis: {e}")


# Global connection manager
connection_manager = ConnectionManager()
