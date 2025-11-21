from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from ..database import get_db
from ..auth.dependencies import get_current_user
from ..models.user import User
from ..models.notification import NotificationCategory, NotificationType, NotificationPriority
from ..schemas.notification import (
    NotificationResponse, NotificationListResponse, NotificationUpdate,
    NotificationPreferenceResponse, NotificationPreferencesResponse,
    NotificationPreferenceUpdate, BulkNotificationCreate,
    NotificationStatsResponse, SendNotificationRequest
)
from ..services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["notifications"])
notification_service = NotificationService()


@router.get("/", response_model=NotificationListResponse)
async def get_notifications(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    unread_only: bool = Query(False),
    category: Optional[NotificationCategory] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get notifications for the current user"""
    try:
        result = notification_service.get_user_notifications(
            db=db,
            user_id=current_user.id,
            limit=limit,
            offset=offset,
            unread_only=unread_only
        )
        
        # Filter by category if specified
        notifications = result['notifications']
        if category:
            notifications = [n for n in notifications if n.category == category]
        
        return NotificationListResponse(
            notifications=notifications,
            total=result['total'],
            unread_count=result['unread_count']
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get notifications: {str(e)}")


@router.get("/{notification_id}", response_model=NotificationResponse)
async def get_notification(
    notification_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific notification"""
    from ..models.notification import Notification
    
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return notification


@router.patch("/{notification_id}", response_model=NotificationResponse)
async def update_notification(
    notification_id: UUID,
    update_data: NotificationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a notification (e.g., mark as read)"""
    from ..models.notification import Notification
    from datetime import datetime
    
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    # Update fields
    if update_data.status:
        notification.status = update_data.status
    
    if update_data.read_at:
        notification.read_at = update_data.read_at
    elif update_data.status and 'read' in update_data.status.value.lower():
        notification.read_at = datetime.utcnow()
    
    db.commit()
    db.refresh(notification)
    
    return notification


@router.post("/{notification_id}/mark-read", response_model=NotificationResponse)
async def mark_notification_read(
    notification_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark a notification as read"""
    success = notification_service.mark_notification_as_read(
        db=db,
        notification_id=notification_id,
        user_id=current_user.id
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found or already read")
    
    # Return updated notification
    from ..models.notification import Notification
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    return notification


@router.post("/mark-all-read")
async def mark_all_notifications_read(
    category: Optional[NotificationCategory] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark all notifications as read for the current user"""
    from ..models.notification import Notification
    from sqlalchemy import and_
    from datetime import datetime
    
    try:
        query = db.query(Notification).filter(
            and_(
                Notification.user_id == current_user.id,
                Notification.read_at.is_(None)
            )
        )
        
        if category:
            query = query.filter(Notification.category == category)
        
        updated_count = query.update({
            'read_at': datetime.utcnow(),
            'status': 'read'
        })
        
        db.commit()
        
        return {
            'success': True,
            'message': f'Marked {updated_count} notifications as read'
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to mark notifications as read: {str(e)}")


@router.get("/preferences/", response_model=NotificationPreferencesResponse)
async def get_notification_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get notification preferences for the current user"""
    from ..models.notification import NotificationPreference
    
    preferences = db.query(NotificationPreference).filter(
        NotificationPreference.user_id == current_user.id
    ).all()
    
    return NotificationPreferencesResponse(preferences=preferences)


@router.put("/preferences/{category}", response_model=NotificationPreferenceResponse)
async def update_notification_preference(
    category: NotificationCategory,
    preference_data: NotificationPreferenceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update notification preferences for a specific category"""
    from ..models.notification import NotificationPreference
    from datetime import datetime
    
    # Get or create preference
    preference = db.query(NotificationPreference).filter(
        NotificationPreference.user_id == current_user.id,
        NotificationPreference.category == category
    ).first()
    
    if not preference:
        preference = NotificationPreference(
            user_id=current_user.id,
            category=category
        )
        db.add(preference)
    
    # Update fields
    for field, value in preference_data.dict(exclude_unset=True).items():
        setattr(preference, field, value)
    
    preference.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(preference)
    
    return preference


@router.get("/stats/", response_model=NotificationStatsResponse)
async def get_notification_stats(
    category: Optional[NotificationCategory] = Query(None),
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get notification statistics for the current user"""
    stats = notification_service.get_notification_stats(
        db=db,
        user_id=current_user.id,
        category=category,
        days=days
    )
    
    return NotificationStatsResponse(**stats)


# Admin endpoints (require admin role)
@router.post("/send", dependencies=[Depends(get_current_user)])
async def send_notification(
    request: SendNotificationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Send notification to specified users (admin only)"""
    # Check if user is admin
    if current_user.user_type.value != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        # Create and send notifications in background
        background_tasks.add_task(
            _send_bulk_notifications_task,
            db,
            request
        )
        
        return {
            'success': True,
            'message': f'Notification queued for {len(request.user_ids)} users'
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to queue notifications: {str(e)}")


@router.post("/bulk", dependencies=[Depends(get_current_user)])
async def send_bulk_notifications(
    request: BulkNotificationCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Send bulk notifications (admin only)"""
    # Check if user is admin
    if current_user.user_type.value != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        # Send notifications in background
        background_tasks.add_task(
            notification_service.send_bulk_notifications,
            db,
            request.user_ids,
            request.title,
            request.message,
            request.category,
            request.type,
            request.priority,
            request.data
        )
        
        return {
            'success': True,
            'message': f'Bulk notification queued for {len(request.user_ids)} users'
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to queue bulk notifications: {str(e)}")


@router.get("/admin/stats", dependencies=[Depends(get_current_user)])
async def get_admin_notification_stats(
    category: Optional[NotificationCategory] = Query(None),
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get platform-wide notification statistics (admin only)"""
    # Check if user is admin
    if current_user.user_type.value != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    stats = notification_service.get_notification_stats(
        db=db,
        user_id=None,  # Platform-wide stats
        category=category,
        days=days
    )
    
    return NotificationStatsResponse(**stats)


async def _send_bulk_notifications_task(db: Session, request: SendNotificationRequest):
    """Background task to send bulk notifications"""
    try:
        if request.template_name:
            # Use template (implementation would require template service)
            # For now, use title/message directly
            pass
        
        await notification_service.send_bulk_notifications(
            db=db,
            user_ids=request.user_ids,
            title=request.title or "Notification",
            message=request.message or "You have a new notification",
            category=request.category,
            notification_type=request.type,
            priority=request.priority,
            data=request.template_variables
        )
        
    except Exception as e:
        # Log error (in production, you might want to use a proper logging system)
        print(f"Failed to send bulk notifications: {str(e)}")


# WebSocket endpoint for real-time notifications
@router.websocket("/ws/{user_id}")
async def websocket_notifications(websocket, user_id: UUID):
    """WebSocket endpoint for real-time notification updates"""
    # This would be implemented with WebSocket manager
    # For now, it's a placeholder
    await websocket.accept()
    try:
        while True:
            # Listen for new notifications and send to client
            await websocket.receive_text()
            # Implementation would check for new notifications and send them
            await websocket.send_json({
                "type": "notification",
                "data": {"message": "New notification available"}
            })
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()