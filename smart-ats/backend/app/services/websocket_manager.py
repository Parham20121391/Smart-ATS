# smart-ats/backend/app/services/websocket_manager.py
from typing import List
from fastapi import WebSocket
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    """
    مدیریت اتصالات فعال وب‌سوکت و برادکست وقایع به کلاینت‌های متصل
    (تسک ۳۹ و ۴۰)
    """
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket client connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket client disconnected. Remaining connections: {len(self.active_connections)}")

    async def broadcast_candidate_update(self, candidate_id: int, next_state: str):
        """
        مخابره واقعه تغییر وضعیت کاندیدا به تمام کلاینت‌ها
        """
        message = {
            "event": "CANDIDATE_STATUS_UPDATED",
            "data": {
                "candidate_id": candidate_id,
                "current_status": next_state
            }
        }
        disconnected_clients = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"Failed to send WS message, scheduling cleanup: {e}")
                disconnected_clients.append(connection)

        # پاکسازی کانکشن‌های قطع شده
        for dead_connection in disconnected_clients:
            self.disconnect(dead_connection)

ws_manager = ConnectionManager()