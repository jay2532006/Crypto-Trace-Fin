# backend/api/ws_routes.py
"""
CryptoTrace LEA — WebSocket Live Forensic Trace Stream (§8.6)
Provides real-time pub/sub event broadcasting for active investigative traces:
- WS /ws/trace/{case_id}
Emits: HOP_COMPLETE, VASP_IDENTIFIED, TYPOLOGY_DETECTED, MIXER_BOUNDARY, TRACE_COMPLETE
"""

import asyncio
import logging
from typing import Dict, Set, Any, Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger("cryptotrace.ws")
router = APIRouter(tags=["WebSocket Stream"])


class TraceStreamManager:
    """Manages active investigator WebSocket connections partitioned by case_id."""

    def __init__(self):
        self._connections: Dict[str, Set[WebSocket]] = {}
        self._lock = asyncio.Lock() if asyncio.get_event_loop().is_running() else None

    async def connect(self, case_id: str, websocket: WebSocket):
        await websocket.accept()
        key = case_id.strip().upper()
        if key not in self._connections:
            self._connections[key] = set()
        self._connections[key].add(websocket)
        logger.info(f"WebSocket client connected to case {key}. Total: {len(self._connections[key])}")

    def disconnect(self, case_id: str, websocket: WebSocket):
        key = case_id.strip().upper()
        if key in self._connections:
            self._connections[key].discard(websocket)
            if not self._connections[key]:
                del self._connections[key]
        logger.info(f"WebSocket client disconnected from case {key}")

    async def broadcast(self, case_id: str, event_data: Dict[str, Any]):
        key = case_id.strip().upper()
        clients = self._connections.get(key)
        if not clients:
            return

        dead_clients: Set[WebSocket] = set()
        for client in list(clients):
            try:
                await client.send_json(event_data)
            except Exception as exc:
                logger.debug(f"Failed sending event to WS client in case {key}: {exc}")
                dead_clients.add(client)

        for dead in dead_clients:
            self.disconnect(case_id, dead)


trace_stream_manager = TraceStreamManager()


def emit_trace_event(case_id: str, event_data: Dict[str, Any]):
    """
    Synchronous / asynchronous bridge hook callable from within BFS tracing loop.
    Schedules broadcast on the active event loop without blocking synchronous tracer.
    """
    try:
        loop = asyncio.get_running_loop()
        if loop.is_running():
            asyncio.run_coroutine_threadsafe(
                trace_stream_manager.broadcast(case_id, event_data), loop
            )
    except RuntimeError:
        pass


@router.websocket("/ws/trace/{case_id}")
async def websocket_trace_feed(websocket: WebSocket, case_id: str):
    """
    §8.6: Subscribes frontend clients to live hop-by-hop forensic events.
    """
    await trace_stream_manager.connect(case_id, websocket)
    try:
        await websocket.send_json({
            "event": "CONNECTED",
            "case_id": case_id,
            "message": f"Subscribed to live forensic trace stream for case {case_id}",
        })
        while True:
            # Keep listener open and respond to heartbeats
            data = await websocket.receive_text()
            if data.lower() == "ping":
                await websocket.send_json({"event": "PONG", "case_id": case_id})
    except WebSocketDisconnect:
        trace_stream_manager.disconnect(case_id, websocket)
    except Exception as exc:
        logger.debug(f"WS error for case {case_id}: {exc}")
        trace_stream_manager.disconnect(case_id, websocket)
