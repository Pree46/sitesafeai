from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from datetime import datetime
import logging

logger = logging.getLogger("sitesafeai")

websocket_router = APIRouter()
connected_clients = []

async def broadcast_alert(message):
    payload = {
        "message": message,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    }
    disconnected = []
    
    for ws in connected_clients:
        try:
            await ws.send_json(payload)
        except Exception as e:
            logger.error(f"Failed to send alert to client: {e}")
            disconnected.append(ws)
    
    # Remove disconnected clients
    for ws in disconnected:
        if ws in connected_clients:
            connected_clients.remove(ws)

@websocket_router.websocket("/ws/alerts")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    connected_clients.append(ws)
    logger.info(f"WebSocket client connected. Total clients: {len(connected_clients)}")
    
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        if ws in connected_clients:
            connected_clients.remove(ws)
        logger.info(f"WebSocket client disconnected. Total clients: {len(connected_clients)}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if ws in connected_clients:
            connected_clients.remove(ws)
