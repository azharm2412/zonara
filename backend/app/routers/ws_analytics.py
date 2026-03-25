"""
@module WSAnalytics
@desc WebSocket endpoint untuk live-sync data analitik ke Focus Mode.
      Mengacu pada FR-004 (WebSocket Live-Sync).

      Fitur:
      - Accept koneksi per session_id
      - In-memory connection manager (ConnectionManager)
      - Broadcast score_update ke semua client pada sesi tertentu
      - Auto-close koneksi stale

@author Azhar Maulana
@date 25 Maret 2026
@version 1.0
"""

import json
import logging
from typing import Dict, List

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)
router = APIRouter()


class ConnectionManager:
    """
    Mengelola koneksi WebSocket aktif per sesi permainan.
    Menggunakan in-memory dict — cocok untuk single-instance deployment.

    Attributes:
        active_connections (dict): Mapping session_id → list of WebSocket.
    """

    def __init__(self):
        """Inisialisasi connection store."""
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, session_id: int, websocket: WebSocket):
        """
        Menerima koneksi WebSocket dan mendaftarkannya ke sesi.

        @param session_id: ID sesi permainan.
        @param websocket: Instance WebSocket yang baru terhubung.
        """
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = []
        self.active_connections[session_id].append(websocket)
        logger.info(
            "WS client connected to session %d (total: %d)",
            session_id,
            len(self.active_connections[session_id]),
        )

    def disconnect(self, session_id: int, websocket: WebSocket):
        """
        Menghapus koneksi WebSocket dari sesi.

        @param session_id: ID sesi permainan.
        @param websocket: Instance WebSocket yang terputus.
        """
        if session_id in self.active_connections:
            self.active_connections[session_id] = [
                ws for ws in self.active_connections[session_id] if ws != websocket
            ]
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]
        logger.info("WS client disconnected from session %d", session_id)

    async def broadcast_to_session(self, session_id: int, message: dict):
        """
        Mengirim pesan JSON ke semua WebSocket client pada sesi tertentu.
        Client yang sudah terputus akan otomatis di-remove.

        @param session_id: ID sesi target.
        @param message: Dict pesan yang akan di-serialize ke JSON.
        """
        if session_id not in self.active_connections:
            return

        stale_connections = []
        json_message = json.dumps(message)

        for ws in self.active_connections[session_id]:
            try:
                await ws.send_text(json_message)
            except Exception:
                stale_connections.append(ws)

        # Bersihkan koneksi stale
        for ws in stale_connections:
            self.disconnect(session_id, ws)

        if self.active_connections.get(session_id):
            logger.debug(
                "Broadcasted to %d clients on session %d",
                len(self.active_connections[session_id]),
                session_id,
            )


# Singleton instance — digunakan oleh scoring_service
manager = ConnectionManager()


@router.websocket("/{session_id}")
async def websocket_analytics(websocket: WebSocket, session_id: int):
    """
    WebSocket endpoint untuk Focus Mode live-sync.
    Client terhubung → menerima update setiap kali skor baru dicatat.

    Message format yang dikirim:
    {
        "event": "score_update",
        "data": {
            "radar_data": {"blue": 3, "green": 2, "yellow": 3, "red": 1},
            "total_scans": 9
        }
    }

    @param websocket: Instance WebSocket dari client.
    @param session_id: ID sesi permainan yang di-subscribe.
    """
    await manager.connect(session_id, websocket)
    try:
        # Keep connection alive — menunggu client disconnect
        while True:
            # Menerima pesan dari client (untuk keep-alive ping)
            data = await websocket.receive_text()
            # Bisa juga implementasi request manual refresh di sini
            if data == "ping":
                await websocket.send_text(json.dumps({"event": "pong"}))
    except WebSocketDisconnect:
        manager.disconnect(session_id, websocket)
    except Exception:
        manager.disconnect(session_id, websocket)
