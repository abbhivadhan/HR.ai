"""
Webhook Service

Handles webhook management, event delivery, and retry logic.
"""

from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json
import hmac
import hashlib
import uuid
import asyncio
import httpx
import logging
from enum import Enum

from ..models.user import User

logger = logging.getLogger(__name__)


class WebhookStatus(str, Enum):
    """Webhook endpoint status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    FAILED = "failed"
    DISABLED = "disabled"


class WebhookEndpoint:
    """Webhook endpoint model (simplified for demo)"""
    
    def __init__(self, id: str, user_id: str, url: str, events: List[str], 
                 secret: Optional[str] = None, description: Optional[str] = None,
                 is_active: bool = True):
        self.id = id
        self.user_id = user_id
        self.url = url
        self.events = events
        self.secret = secret
        self.description = description
        self.is_active = is_active
        self.status = WebhookStatus.ACTIVE
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.last_delivery_at = None
        self.success_rate = 1.0
        self.total_deliveries = 0
        self.failed_deliveries = 0


class WebhookDeliveryRecord:
    """Webhook delivery record model (simplified for demo)"""
    
    def __init__(self, webhook_id: str, event_type: str, payload: Dict[str, Any]):
        self.id = str(uuid.uuid4())
        self.webhook_id = webhook_id
        self.event_type = event_type
        self.payload = payload
        self.status_code = None
        self.response_body = None
        self.delivery_time_ms = None
        self.attempts = 0
        self.max_attempts = 3
        self.next_retry_at = None
        self.delivered_at = None
        self.created_at = datetime.now()


class WebhookService:
    """Service for managing webhook endpoints"""
    
    def __init__(self, db: Session):
        self.db = db
        self._webhooks: Dict[str, WebhookEndpoint] = {}  # In-memory storage for demo
    
    async def create_webhook(self, user_id: str, webhook_data) -> WebhookEndpoint:
        """Create a new webhook endpoint"""
        
        webhook_id = str(uuid.uuid4())
        webhook = WebhookEndpoint(
            id=webhook_id,
            user_id=user_id,
            url=str(webhook_data.url),
            events=webhook_data.events,
            secret=webhook_data.secret,
            description=webhook_data.description,
            is_active=webhook_data.is_active
        )
        
        self._webhooks[webhook_id] = webhook
        logger.info(f"Created webhook {webhook_id} for user {user_id}")
        
        return webhook
    
    async def get_user_webhooks(self, user_id: str) -> List[WebhookEndpoint]:
        """Get all webhooks for a user"""
        
        return [
            webhook for webhook in self._webhooks.values()
            if webhook.user_id == user_id
        ]
    
    async def get_webhook(self, webhook_id: str, user_id: str) -> Optional[WebhookEndpoint]:
        """Get a specific webhook"""
        
        webhook = self._webhooks.get(webhook_id)
        if webhook and webhook.user_id == user_id:
            return webhook
        return None
    
    async def update_webhook(self, webhook_id: str, user_id: str, webhook_data) -> Optional[WebhookEndpoint]:
        """Update a webhook endpoint"""
        
        webhook = await self.get_webhook(webhook_id, user_id)
        if not webhook:
            return None
        
        if webhook_data.url is not None:
            webhook.url = str(webhook_data.url)
        if webhook_data.events is not None:
            webhook.events = webhook_data.events
        if webhook_data.secret is not None:
            webhook.secret = webhook_data.secret
        if webhook_data.description is not None:
            webhook.description = webhook_data.description
        if webhook_data.is_active is not None:
            webhook.is_active = webhook_data.is_active
        
        webhook.updated_at = datetime.now()
        
        logger.info(f"Updated webhook {webhook_id}")
        return webhook
    
    async def delete_webhook(self, webhook_id: str, user_id: str) -> bool:
        """Delete a webhook endpoint"""
        
        webhook = await self.get_webhook(webhook_id, user_id)
        if not webhook:
            return False
        
        del self._webhooks[webhook_id]
        logger.info(f"Deleted webhook {webhook_id}")
        return True
    
    async def get_webhooks_for_event(self, event_type: str) -> List[WebhookEndpoint]:
        """Get all active webhooks subscribed to an event type"""
        
        return [
            webhook for webhook in self._webhooks.values()
            if webhook.is_active and event_type in webhook.events
        ]
    
    async def get_webhook_deliveries(self, webhook_id: str, limit: int = 50, offset: int = 0) -> List[WebhookDeliveryRecord]:
        """Get delivery history for a webhook (mock implementation)"""
        
        # In a real implementation, this would query the database
        # For demo purposes, returning empty list
        return []


class WebhookDeliveryService:
    """Service for delivering webhook events"""
    
    def __init__(self, db: Session):
        self.db = db
        self._delivery_records: Dict[str, WebhookDeliveryRecord] = {}  # In-memory storage for demo
        self.timeout = 30.0  # 30 seconds timeout
        self.retry_delays = [60, 300, 1800]  # 1 min, 5 min, 30 min
    
    async def deliver_webhook(self, webhook: WebhookEndpoint, event) -> bool:
        """Deliver a webhook event"""
        
        delivery_record = WebhookDeliveryRecord(
            webhook_id=webhook.id,
            event_type=event.event_type,
            payload=event.dict()
        )
        
        self._delivery_records[delivery_record.id] = delivery_record
        
        success = await self._attempt_delivery(webhook, delivery_record)
        
        if success:
            webhook.last_delivery_at = datetime.now()
            webhook.total_deliveries += 1
        else:
            webhook.failed_deliveries += 1
            # Schedule retry if not exceeded max attempts
            if delivery_record.attempts < delivery_record.max_attempts:
                await self._schedule_retry(delivery_record)
        
        # Update success rate
        if webhook.total_deliveries > 0:
            webhook.success_rate = 1.0 - (webhook.failed_deliveries / webhook.total_deliveries)
        
        return success
    
    async def _attempt_delivery(self, webhook: WebhookEndpoint, delivery_record: WebhookDeliveryRecord) -> bool:
        """Attempt to deliver webhook"""
        
        delivery_record.attempts += 1
        start_time = datetime.now()
        
        try:
            # Prepare payload
            payload = {
                "id": str(uuid.uuid4()),
                "event_type": delivery_record.event_type,
                "timestamp": datetime.now().isoformat(),
                "data": delivery_record.payload.get("data", {})
            }
            
            # Prepare headers
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "AI-HR-Platform-Webhook/1.0",
                "X-Webhook-Event": delivery_record.event_type,
                "X-Webhook-Delivery": delivery_record.id
            }
            
            # Add signature if secret is provided
            if webhook.secret:
                payload_str = json.dumps(payload, separators=(',', ':'))
                signature = hmac.new(
                    webhook.secret.encode(),
                    payload_str.encode(),
                    hashlib.sha256
                ).hexdigest()
                headers["X-Webhook-Signature"] = f"sha256={signature}"
            
            # Make HTTP request
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    webhook.url,
                    json=payload,
                    headers=headers
                )
            
            # Calculate delivery time
            delivery_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # Update delivery record
            delivery_record.status_code = response.status_code
            delivery_record.response_body = response.text[:1000]  # Limit response size
            delivery_record.delivery_time_ms = delivery_time
            
            # Check if delivery was successful
            if 200 <= response.status_code < 300:
                delivery_record.delivered_at = datetime.now()
                logger.info(f"Webhook delivered successfully: {webhook.id} -> {webhook.url}")
                return True
            else:
                logger.warning(f"Webhook delivery failed with status {response.status_code}: {webhook.id}")
                return False
                
        except httpx.TimeoutException:
            delivery_record.response_body = "Request timeout"
            logger.warning(f"Webhook delivery timeout: {webhook.id} -> {webhook.url}")
            return False
            
        except httpx.RequestError as e:
            delivery_record.response_body = str(e)
            logger.error(f"Webhook delivery error: {webhook.id} -> {webhook.url}: {str(e)}")
            return False
            
        except Exception as e:
            delivery_record.response_body = f"Unexpected error: {str(e)}"
            logger.error(f"Unexpected webhook delivery error: {webhook.id}: {str(e)}")
            return False
    
    async def _schedule_retry(self, delivery_record: WebhookDeliveryRecord):
        """Schedule webhook retry"""
        
        if delivery_record.attempts >= len(self.retry_delays):
            delay = self.retry_delays[-1]  # Use last delay for subsequent retries
        else:
            delay = self.retry_delays[delivery_record.attempts - 1]
        
        delivery_record.next_retry_at = datetime.now() + timedelta(seconds=delay)
        
        logger.info(f"Scheduled webhook retry for delivery {delivery_record.id} in {delay} seconds")
    
    async def retry_delivery(self, delivery_id: str) -> bool:
        """Retry a failed webhook delivery"""
        
        delivery_record = self._delivery_records.get(delivery_id)
        if not delivery_record:
            return False
        
        if delivery_record.delivered_at is not None:
            return False  # Already delivered
        
        if delivery_record.attempts >= delivery_record.max_attempts:
            return False  # Max attempts exceeded
        
        # Get webhook
        webhook_service = WebhookService(self.db)
        webhook = webhook_service._webhooks.get(delivery_record.webhook_id)
        if not webhook:
            return False
        
        # Attempt delivery
        success = await self._attempt_delivery(webhook, delivery_record)
        
        if not success and delivery_record.attempts < delivery_record.max_attempts:
            await self._schedule_retry(delivery_record)
        
        return success
    
    async def process_retry_queue(self):
        """Process webhook retry queue (background task)"""
        
        now = datetime.now()
        
        for delivery_record in self._delivery_records.values():
            if (delivery_record.next_retry_at and 
                delivery_record.next_retry_at <= now and
                delivery_record.delivered_at is None and
                delivery_record.attempts < delivery_record.max_attempts):
                
                # Get webhook
                webhook_service = WebhookService(self.db)
                webhook = webhook_service._webhooks.get(delivery_record.webhook_id)
                
                if webhook:
                    await self._attempt_delivery(webhook, delivery_record)


class WebhookEventDispatcher:
    """Dispatcher for webhook events"""
    
    def __init__(self, db: Session):
        self.db = db
        self.webhook_service = WebhookService(db)
        self.delivery_service = WebhookDeliveryService(db)
    
    async def dispatch_event(self, event_type: str, event_data: Dict[str, Any], user_id: Optional[str] = None):
        """Dispatch an event to all subscribed webhooks"""
        
        # Get webhooks subscribed to this event type
        webhooks = await self.webhook_service.get_webhooks_for_event(event_type)
        
        # Filter by user if specified
        if user_id:
            webhooks = [w for w in webhooks if w.user_id == user_id]
        
        # Create event object
        from ..api.webhooks import WebhookEvent
        event = WebhookEvent(
            event_type=event_type,
            data=event_data,
            user_id=user_id
        )
        
        # Deliver to all webhooks
        delivery_tasks = []
        for webhook in webhooks:
            task = self.delivery_service.deliver_webhook(webhook, event)
            delivery_tasks.append(task)
        
        # Execute deliveries concurrently
        if delivery_tasks:
            results = await asyncio.gather(*delivery_tasks, return_exceptions=True)
            successful_deliveries = sum(1 for result in results if result is True)
            
            logger.info(f"Dispatched event {event_type} to {len(webhooks)} webhooks, {successful_deliveries} successful")
        
        return len(webhooks)


# Global event dispatcher instance
_event_dispatcher = None

def get_event_dispatcher(db: Session) -> WebhookEventDispatcher:
    """Get global event dispatcher instance"""
    global _event_dispatcher
    if _event_dispatcher is None:
        _event_dispatcher = WebhookEventDispatcher(db)
    return _event_dispatcher