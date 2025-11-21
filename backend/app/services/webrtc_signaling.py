"""
WebRTC signaling service for video interview sessions
"""
import json
import logging
import secrets
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..models.interview import InterviewSession, SessionStatus, Interview
from ..database import get_db
from .websocket_manager import connection_manager

logger = logging.getLogger(__name__)


class WebRTCSignalingService:
    """Handles WebRTC signaling for video interviews"""
    
    def __init__(self):
        # Store ICE candidates temporarily until both peers are connected
        self.pending_ice_candidates: Dict[str, List[Dict]] = {}
        # Store offers/answers temporarily
        self.pending_offers: Dict[str, Dict] = {}
        # Connection quality monitoring
        self.connection_metrics: Dict[str, Dict] = {}
    
    async def create_session(self, db: Session, interview_id: str) -> Optional[InterviewSession]:
        """Create a new WebRTC session for an interview"""
        try:
            # Check if interview exists and is valid
            interview = db.query(Interview).filter(Interview.id == interview_id).first()
            if not interview:
                logger.error(f"Interview not found: {interview_id}")
                return None
            
            # Generate unique session token and room ID
            session_token = secrets.token_urlsafe(32)
            room_id = f"interview_{interview_id}_{secrets.token_urlsafe(8)}"
            
            # Create session record
            session = InterviewSession(
                interview_id=interview_id,
                session_token=session_token,
                room_id=room_id,
                status=SessionStatus.WAITING,
                signaling_server="internal",
                error_count=0,
                reconnection_attempts=0
            )
            
            db.add(session)
            db.commit()
            db.refresh(session)
            
            # Initialize tracking structures
            self.pending_ice_candidates[room_id] = []
            self.connection_metrics[room_id] = {
                "created_at": datetime.now(),
                "participants": {},
                "quality_reports": []
            }
            
            logger.info(f"Created WebRTC session: {session.id} for interview {interview_id}")
            return session
            
        except Exception as e:
            logger.error(f"Error creating WebRTC session: {e}")
            db.rollback()
            return None
    
    async def join_session(self, db: Session, session_token: str, user_id: str, user_type: str = "candidate") -> Optional[Dict]:
        """Join a WebRTC session"""
        try:
            # Find session by token
            session = db.query(InterviewSession).filter(
                InterviewSession.session_token == session_token
            ).first()
            
            if not session:
                logger.error(f"Session not found for token: {session_token}")
                return None
            
            # Check if session is in valid state
            if session.status not in [SessionStatus.WAITING, SessionStatus.CONNECTING]:
                logger.error(f"Session {session.id} is not in joinable state: {session.status}")
                return None
            
            # Update session status
            if session.status == SessionStatus.WAITING:
                session.status = SessionStatus.CONNECTING
                session.joined_at = datetime.now()
            
            # Set peer ID based on user type
            peer_id = f"{user_type}_{user_id}_{secrets.token_urlsafe(8)}"
            
            if user_type == "candidate":
                session.candidate_peer_id = peer_id
            else:
                session.ai_peer_id = peer_id
            
            session.last_activity_at = datetime.now()
            db.commit()
            
            # Add to connection metrics
            if session.room_id in self.connection_metrics:
                self.connection_metrics[session.room_id]["participants"][user_id] = {
                    "peer_id": peer_id,
                    "user_type": user_type,
                    "joined_at": datetime.now(),
                    "connection_state": "connecting"
                }
            
            return {
                "session_id": str(session.id),
                "room_id": session.room_id,
                "peer_id": peer_id,
                "signaling_server": session.signaling_server,
                "ice_servers": self._get_ice_servers(),
                "session_config": {
                    "recording_enabled": session.interview.recording_enabled,
                    "max_duration": session.interview.duration_minutes * 60 if session.interview.duration_minutes else 3600
                }
            }
            
        except Exception as e:
            logger.error(f"Error joining session: {e}")
            db.rollback()
            return None
    
    async def handle_signaling_message(self, db: Session, room_id: str, sender_peer_id: str, message: Dict) -> bool:
        """Handle WebRTC signaling messages"""
        try:
            message_type = message.get("type")
            
            if message_type == "offer":
                return await self._handle_offer(db, room_id, sender_peer_id, message)
            elif message_type == "answer":
                return await self._handle_answer(db, room_id, sender_peer_id, message)
            elif message_type == "ice-candidate":
                return await self._handle_ice_candidate(db, room_id, sender_peer_id, message)
            elif message_type == "connection-state":
                return await self._handle_connection_state(db, room_id, sender_peer_id, message)
            elif message_type == "quality-report":
                return await self._handle_quality_report(db, room_id, sender_peer_id, message)
            else:
                logger.warning(f"Unknown signaling message type: {message_type}")
                return False
                
        except Exception as e:
            logger.error(f"Error handling signaling message: {e}")
            return False
    
    async def _handle_offer(self, db: Session, room_id: str, sender_peer_id: str, message: Dict) -> bool:
        """Handle WebRTC offer"""
        try:
            # Store the offer
            self.pending_offers[f"{room_id}_{sender_peer_id}"] = message
            
            # Forward to other participants in the room
            signaling_message = {
                "type": "offer",
                "from_peer": sender_peer_id,
                "sdp": message.get("sdp"),
                "timestamp": datetime.now().isoformat()
            }
            
            await connection_manager.broadcast_to_room(
                room_id, 
                {"type": "signaling", "data": signaling_message},
                exclude_session=sender_peer_id
            )
            
            logger.debug(f"Forwarded offer from {sender_peer_id} in room {room_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error handling offer: {e}")
            return False
    
    async def _handle_answer(self, db: Session, room_id: str, sender_peer_id: str, message: Dict) -> bool:
        """Handle WebRTC answer"""
        try:
            # Forward to the peer who sent the offer
            target_peer = message.get("to_peer")
            
            signaling_message = {
                "type": "answer",
                "from_peer": sender_peer_id,
                "to_peer": target_peer,
                "sdp": message.get("sdp"),
                "timestamp": datetime.now().isoformat()
            }
            
            # Send to specific peer if specified, otherwise broadcast
            if target_peer:
                # Find the session for the target peer
                for session_id, connection_info in connection_manager.rooms.get(room_id, {}).items():
                    if connection_info.get("peer_id") == target_peer:
                        await connection_manager.send_personal_message(
                            {"type": "signaling", "data": signaling_message},
                            session_id
                        )
                        break
            else:
                await connection_manager.broadcast_to_room(
                    room_id,
                    {"type": "signaling", "data": signaling_message},
                    exclude_session=sender_peer_id
                )
            
            logger.debug(f"Forwarded answer from {sender_peer_id} in room {room_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error handling answer: {e}")
            return False
    
    async def _handle_ice_candidate(self, db: Session, room_id: str, sender_peer_id: str, message: Dict) -> bool:
        """Handle ICE candidate"""
        try:
            # Store ICE candidate
            if room_id not in self.pending_ice_candidates:
                self.pending_ice_candidates[room_id] = []
            
            ice_candidate = {
                "from_peer": sender_peer_id,
                "candidate": message.get("candidate"),
                "sdpMid": message.get("sdpMid"),
                "sdpMLineIndex": message.get("sdpMLineIndex"),
                "timestamp": datetime.now().isoformat()
            }
            
            self.pending_ice_candidates[room_id].append(ice_candidate)
            
            # Forward to other participants
            signaling_message = {
                "type": "ice-candidate",
                **ice_candidate
            }
            
            await connection_manager.broadcast_to_room(
                room_id,
                {"type": "signaling", "data": signaling_message},
                exclude_session=sender_peer_id
            )
            
            logger.debug(f"Forwarded ICE candidate from {sender_peer_id} in room {room_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error handling ICE candidate: {e}")
            return False
    
    async def _handle_connection_state(self, db: Session, room_id: str, sender_peer_id: str, message: Dict) -> bool:
        """Handle connection state updates"""
        try:
            connection_state = message.get("state")
            
            # Update session status based on connection state
            session = db.query(InterviewSession).filter(
                InterviewSession.room_id == room_id
            ).first()
            
            if session:
                if connection_state == "connected":
                    if session.status == SessionStatus.CONNECTING:
                        session.status = SessionStatus.CONNECTED
                        session.started_at = datetime.now()
                elif connection_state == "disconnected":
                    session.status = SessionStatus.ERROR
                    session.error_count += 1
                elif connection_state == "failed":
                    session.status = SessionStatus.ERROR
                    session.error_count += 1
                    session.last_error = "Connection failed"
                
                session.last_activity_at = datetime.now()
                db.commit()
            
            # Update metrics
            if room_id in self.connection_metrics:
                for user_id, participant in self.connection_metrics[room_id]["participants"].items():
                    if participant["peer_id"] == sender_peer_id:
                        participant["connection_state"] = connection_state
                        break
            
            # Notify other participants
            await connection_manager.broadcast_to_room(
                room_id,
                {
                    "type": "peer_connection_state",
                    "peer_id": sender_peer_id,
                    "state": connection_state,
                    "timestamp": datetime.now().isoformat()
                },
                exclude_session=sender_peer_id
            )
            
            logger.info(f"Connection state update: {sender_peer_id} -> {connection_state} in room {room_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error handling connection state: {e}")
            return False
    
    async def _handle_quality_report(self, db: Session, room_id: str, sender_peer_id: str, message: Dict) -> bool:
        """Handle connection quality reports"""
        try:
            quality_data = message.get("quality", {})
            
            # Update session with quality metrics
            session = db.query(InterviewSession).filter(
                InterviewSession.room_id == room_id
            ).first()
            
            if session:
                # Update quality metrics
                session.connection_quality = quality_data.get("connection_quality")
                session.audio_quality = quality_data.get("audio_quality")
                session.video_quality = quality_data.get("video_quality")
                session.latency_ms = quality_data.get("latency_ms")
                session.last_activity_at = datetime.now()
                db.commit()
            
            # Store in metrics for analysis
            if room_id in self.connection_metrics:
                self.connection_metrics[room_id]["quality_reports"].append({
                    "peer_id": sender_peer_id,
                    "timestamp": datetime.now(),
                    "quality": quality_data
                })
            
            logger.debug(f"Quality report from {sender_peer_id}: {quality_data}")
            return True
            
        except Exception as e:
            logger.error(f"Error handling quality report: {e}")
            return False
    
    async def end_session(self, db: Session, room_id: str, reason: str = "completed") -> bool:
        """End a WebRTC session"""
        try:
            # Update session status
            session = db.query(InterviewSession).filter(
                InterviewSession.room_id == room_id
            ).first()
            
            if session:
                session.status = SessionStatus.ENDED
                session.ended_at = datetime.now()
                if reason != "completed":
                    session.last_error = reason
                db.commit()
            
            # Notify all participants
            await connection_manager.broadcast_to_room(
                room_id,
                {
                    "type": "session_ended",
                    "reason": reason,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            # Clean up tracking data
            self.pending_ice_candidates.pop(room_id, None)
            self.connection_metrics.pop(room_id, None)
            
            # Remove all participants from the room
            if room_id in connection_manager.rooms:
                for session_id in list(connection_manager.rooms[room_id].keys()):
                    await connection_manager.leave_room(session_id, room_id)
            
            logger.info(f"Ended WebRTC session for room {room_id}: {reason}")
            return True
            
        except Exception as e:
            logger.error(f"Error ending session: {e}")
            return False
    
    def _get_ice_servers(self) -> List[Dict]:
        """Get ICE servers configuration"""
        # In production, you would use TURN servers for NAT traversal
        return [
            {"urls": "stun:stun.l.google.com:19302"},
            {"urls": "stun:stun1.l.google.com:19302"},
            # Add TURN servers for production:
            # {
            #     "urls": "turn:your-turn-server.com:3478",
            #     "username": "your-username",
            #     "credential": "your-password"
            # }
        ]
    
    def get_session_metrics(self, room_id: str) -> Optional[Dict]:
        """Get metrics for a session"""
        return self.connection_metrics.get(room_id)
    
    async def handle_reconnection(self, db: Session, room_id: str, peer_id: str) -> bool:
        """Handle peer reconnection"""
        try:
            session = db.query(InterviewSession).filter(
                InterviewSession.room_id == room_id
            ).first()
            
            if session:
                session.reconnection_attempts += 1
                session.status = SessionStatus.CONNECTING
                session.last_activity_at = datetime.now()
                db.commit()
            
            # Resend pending ICE candidates to the reconnecting peer
            if room_id in self.pending_ice_candidates:
                for ice_candidate in self.pending_ice_candidates[room_id]:
                    if ice_candidate["from_peer"] != peer_id:
                        await connection_manager.send_personal_message(
                            {"type": "signaling", "data": ice_candidate},
                            peer_id
                        )
            
            logger.info(f"Handling reconnection for peer {peer_id} in room {room_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error handling reconnection: {e}")
            return False


# Global signaling service instance
webrtc_signaling = WebRTCSignalingService()