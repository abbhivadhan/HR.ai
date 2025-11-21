"""
WebSocket connection manager for real-time communications
"""
import json
import logging
from typing import Dict, List, Optional, Set
from datetime import datetime
import asyncio
from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from ..models.interview import InterviewSession, SessionStatus
from ..database import get_db

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for interview sessions"""
    
    def __init__(self):
        # Active connections: {session_id: {websocket, user_id, user_type}}
        self.active_connections: Dict[str, Dict] = {}
        # Room connections: {room_id: {session_id: connection_info}}
        self.rooms: Dict[str, Dict[str, Dict]] = {}
        # User connections: {user_id: [session_ids]}
        self.user_sessions: Dict[str, Set[str]] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str, user_id: str, user_type: str = "candidate"):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        
        connection_info = {
            "websocket": websocket,
            "user_id": user_id,
            "user_type": user_type,
            "connected_at": datetime.now(),
            "last_ping": datetime.now()
        }
        
        self.active_connections[session_id] = connection_info
        
        # Add to user sessions tracking
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = set()
        self.user_sessions[user_id].add(session_id)
        
        logger.info(f"WebSocket connected: session_id={session_id}, user_id={user_id}, user_type={user_type}")
    
    def disconnect(self, session_id: str):
        """Remove a WebSocket connection"""
        if session_id in self.active_connections:
            connection_info = self.active_connections[session_id]
            user_id = connection_info["user_id"]
            
            # Remove from active connections
            del self.active_connections[session_id]
            
            # Remove from user sessions
            if user_id in self.user_sessions:
                self.user_sessions[user_id].discard(session_id)
                if not self.user_sessions[user_id]:
                    del self.user_sessions[user_id]
            
            # Remove from rooms
            for room_id, room_connections in self.rooms.items():
                if session_id in room_connections:
                    del room_connections[session_id]
                    break
            
            logger.info(f"WebSocket disconnected: session_id={session_id}, user_id={user_id}")
    
    async def join_room(self, session_id: str, room_id: str):
        """Add a connection to a room"""
        if session_id not in self.active_connections:
            logger.warning(f"Attempted to join room with invalid session: {session_id}")
            return False
        
        if room_id not in self.rooms:
            self.rooms[room_id] = {}
        
        self.rooms[room_id][session_id] = self.active_connections[session_id]
        
        # Notify other participants in the room
        await self.broadcast_to_room(room_id, {
            "type": "user_joined",
            "session_id": session_id,
            "user_id": self.active_connections[session_id]["user_id"],
            "user_type": self.active_connections[session_id]["user_type"],
            "timestamp": datetime.now().isoformat()
        }, exclude_session=session_id)
        
        logger.info(f"Session {session_id} joined room {room_id}")
        return True
    
    async def leave_room(self, session_id: str, room_id: str):
        """Remove a connection from a room"""
        if room_id in self.rooms and session_id in self.rooms[room_id]:
            user_info = self.rooms[room_id][session_id]
            del self.rooms[room_id][session_id]
            
            # Clean up empty rooms
            if not self.rooms[room_id]:
                del self.rooms[room_id]
            
            # Notify other participants
            await self.broadcast_to_room(room_id, {
                "type": "user_left",
                "session_id": session_id,
                "user_id": user_info["user_id"],
                "timestamp": datetime.now().isoformat()
            })
            
            logger.info(f"Session {session_id} left room {room_id}")
    
    async def send_personal_message(self, message: dict, session_id: str):
        """Send a message to a specific session"""
        if session_id in self.active_connections:
            websocket = self.active_connections[session_id]["websocket"]
            try:
                await websocket.send_text(json.dumps(message))
                return True
            except Exception as e:
                logger.error(f"Error sending message to session {session_id}: {e}")
                self.disconnect(session_id)
                return False
        return False
    
    async def broadcast_to_room(self, room_id: str, message: dict, exclude_session: Optional[str] = None):
        """Broadcast a message to all connections in a room"""
        if room_id not in self.rooms:
            return
        
        message["timestamp"] = datetime.now().isoformat()
        disconnected_sessions = []
        
        for session_id, connection_info in self.rooms[room_id].items():
            if exclude_session and session_id == exclude_session:
                continue
            
            try:
                websocket = connection_info["websocket"]
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error broadcasting to session {session_id}: {e}")
                disconnected_sessions.append(session_id)
        
        # Clean up disconnected sessions
        for session_id in disconnected_sessions:
            self.disconnect(session_id)
    
    async def send_to_user(self, user_id: str, message: dict):
        """Send a message to all sessions of a specific user"""
        if user_id not in self.user_sessions:
            return False
        
        success_count = 0
        for session_id in list(self.user_sessions[user_id]):
            if await self.send_personal_message(message, session_id):
                success_count += 1
        
        return success_count > 0
    
    def get_room_participants(self, room_id: str) -> List[Dict]:
        """Get list of participants in a room"""
        if room_id not in self.rooms:
            return []
        
        participants = []
        for session_id, connection_info in self.rooms[room_id].items():
            participants.append({
                "session_id": session_id,
                "user_id": connection_info["user_id"],
                "user_type": connection_info["user_type"],
                "connected_at": connection_info["connected_at"].isoformat()
            })
        
        return participants
    
    def get_connection_stats(self) -> Dict:
        """Get connection statistics"""
        return {
            "total_connections": len(self.active_connections),
            "total_rooms": len(self.rooms),
            "total_users": len(self.user_sessions),
            "rooms": {
                room_id: len(connections) 
                for room_id, connections in self.rooms.items()
            }
        }
    
    async def ping_all_connections(self):
        """Send ping to all connections to check if they're alive"""
        disconnected_sessions = []
        ping_message = {"type": "ping", "timestamp": datetime.now().isoformat()}
        
        for session_id, connection_info in self.active_connections.items():
            try:
                websocket = connection_info["websocket"]
                await websocket.send_text(json.dumps(ping_message))
                connection_info["last_ping"] = datetime.now()
            except Exception as e:
                logger.error(f"Ping failed for session {session_id}: {e}")
                disconnected_sessions.append(session_id)
        
        # Clean up disconnected sessions
        for session_id in disconnected_sessions:
            self.disconnect(session_id)
        
        return len(self.active_connections) - len(disconnected_sessions)


# Global connection manager instance
connection_manager = ConnectionManager()


async def periodic_ping():
    """Periodic task to ping all connections"""
    while True:
        try:
            active_count = await connection_manager.ping_all_connections()
            logger.debug(f"Pinged {active_count} active connections")
        except Exception as e:
            logger.error(f"Error in periodic ping: {e}")
        
        await asyncio.sleep(30)  # Ping every 30 seconds