"""
WebSocket API endpoints for real-time communication
"""
import json
import logging
from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..services.websocket_manager import connection_manager
from ..services.webrtc_signaling import webrtc_signaling
from ..models.interview import InterviewSession
from ..auth.dependencies import get_current_user_websocket

logger = logging.getLogger(__name__)
router = APIRouter()


@router.websocket("/ws/interview/{session_token}")
async def websocket_interview_endpoint(
    websocket: WebSocket,
    session_token: str,
    db: Session = Depends(get_db)
):
    """WebSocket endpoint for interview sessions"""
    session_id = None
    room_id = None
    
    try:
        # Validate session token and get session info
        session = db.query(InterviewSession).filter(
            InterviewSession.session_token == session_token
        ).first()
        
        if not session:
            await websocket.close(code=4004, reason="Invalid session token")
            return
        
        session_id = str(session.id)
        room_id = session.room_id
        
        # For now, we'll extract user info from the session
        # In a real implementation, you'd validate the user token
        user_id = str(session.interview.candidate_id)  # Default to candidate
        user_type = "candidate"
        
        # Accept the WebSocket connection
        await connection_manager.connect(websocket, session_id, user_id, user_type)
        
        # Join the interview room
        await connection_manager.join_room(session_id, room_id)
        
        # Send initial connection confirmation
        await connection_manager.send_personal_message({
            "type": "connection_established",
            "session_id": session_id,
            "room_id": room_id,
            "user_id": user_id,
            "participants": connection_manager.get_room_participants(room_id)
        }, session_id)
        
        # Main message handling loop
        while True:
            try:
                # Receive message from client
                data = await websocket.receive_text()
                message = json.loads(data)
                
                await handle_websocket_message(db, session_id, room_id, user_id, message)
                
            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected: session_id={session_id}")
                break
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON received from session {session_id}")
                await connection_manager.send_personal_message({
                    "type": "error",
                    "message": "Invalid JSON format"
                }, session_id)
            except Exception as e:
                logger.error(f"Error handling WebSocket message: {e}")
                await connection_manager.send_personal_message({
                    "type": "error",
                    "message": "Internal server error"
                }, session_id)
    
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
        if websocket.client_state.name != "DISCONNECTED":
            await websocket.close(code=4000, reason="Internal server error")
    
    finally:
        # Clean up connection
        if session_id:
            connection_manager.disconnect(session_id)
        if room_id and session_id:
            await connection_manager.leave_room(session_id, room_id)


async def handle_websocket_message(
    db: Session,
    session_id: str,
    room_id: str,
    user_id: str,
    message: dict
):
    """Handle incoming WebSocket messages"""
    message_type = message.get("type")
    
    try:
        if message_type == "ping":
            # Respond to ping with pong
            await connection_manager.send_personal_message({
                "type": "pong",
                "timestamp": message.get("timestamp")
            }, session_id)
        
        elif message_type == "signaling":
            # Handle WebRTC signaling messages
            signaling_data = message.get("data", {})
            peer_id = message.get("peer_id", user_id)
            
            await webrtc_signaling.handle_signaling_message(
                db, room_id, peer_id, signaling_data
            )
        
        elif message_type == "chat":
            # Handle chat messages during interview
            chat_message = {
                "type": "chat",
                "from_user": user_id,
                "message": message.get("message", ""),
                "timestamp": message.get("timestamp")
            }
            
            await connection_manager.broadcast_to_room(
                room_id, chat_message, exclude_session=session_id
            )
        
        elif message_type == "interview_action":
            # Handle interview-specific actions
            await handle_interview_action(db, session_id, room_id, user_id, message)
        
        elif message_type == "quality_report":
            # Handle connection quality reports
            await webrtc_signaling.handle_signaling_message(
                db, room_id, user_id, message
            )
        
        else:
            logger.warning(f"Unknown message type: {message_type}")
            await connection_manager.send_personal_message({
                "type": "error",
                "message": f"Unknown message type: {message_type}"
            }, session_id)
    
    except Exception as e:
        logger.error(f"Error handling message type {message_type}: {e}")
        await connection_manager.send_personal_message({
            "type": "error",
            "message": "Failed to process message"
        }, session_id)


async def handle_interview_action(
    db: Session,
    session_id: str,
    room_id: str,
    user_id: str,
    message: dict
):
    """Handle interview-specific actions"""
    action = message.get("action")
    
    if action == "start_recording":
        # Start recording the interview
        await connection_manager.broadcast_to_room(room_id, {
            "type": "recording_started",
            "initiated_by": user_id
        })
        
        # Update session status
        session = db.query(InterviewSession).filter(
            InterviewSession.room_id == room_id
        ).first()
        if session:
            session.status = "recording"
            db.commit()
    
    elif action == "stop_recording":
        # Stop recording the interview
        await connection_manager.broadcast_to_room(room_id, {
            "type": "recording_stopped",
            "initiated_by": user_id
        })
        
        # Update session status
        session = db.query(InterviewSession).filter(
            InterviewSession.room_id == room_id
        ).first()
        if session:
            session.status = "connected"
            db.commit()
    
    elif action == "end_interview":
        # End the interview session
        await webrtc_signaling.end_session(db, room_id, "completed")
    
    elif action == "request_help":
        # Request technical help
        await connection_manager.broadcast_to_room(room_id, {
            "type": "help_requested",
            "requested_by": user_id,
            "issue": message.get("issue", "Technical difficulties")
        })
    
    else:
        logger.warning(f"Unknown interview action: {action}")


@router.get("/ws/stats")
async def get_websocket_stats():
    """Get WebSocket connection statistics"""
    return connection_manager.get_connection_stats()


@router.post("/ws/broadcast/{room_id}")
async def broadcast_to_room(
    room_id: str,
    message: dict,
    db: Session = Depends(get_db)
):
    """Broadcast a message to all participants in a room (admin only)"""
    # In a real implementation, you'd check admin permissions here
    
    await connection_manager.broadcast_to_room(room_id, {
        "type": "admin_message",
        "data": message
    })
    
    return {"status": "Message broadcasted"}


@router.post("/ws/session/{session_token}/end")
async def end_session_api(
    session_token: str,
    reason: str = "completed",
    db: Session = Depends(get_db)
):
    """End a WebSocket session via API"""
    session = db.query(InterviewSession).filter(
        InterviewSession.session_token == session_token
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    success = await webrtc_signaling.end_session(db, session.room_id, reason)
    
    if success:
        return {"status": "Session ended successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to end session"
        )