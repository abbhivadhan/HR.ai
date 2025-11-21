"""
Security API endpoints for MFA, audit logs, and GDPR compliance
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from sqlalchemy.orm import Session
from pydantic import BaseModel
from ..database import get_db
from ..auth.dependencies import get_current_user, get_current_verified_user
from ..models.user import User
from ..services.mfa_service import MFAService
from ..services.audit_service import AuditService
from ..services.gdpr_service import GDPRService
from ..services.security_monitoring_service import SecurityMonitoringService
from ..services.rate_limit_service import rate_limit

router = APIRouter(prefix="/api/security", tags=["security"])


# Pydantic models for request/response
class MFASetupResponse(BaseModel):
    secret_key: str
    qr_code: str


class MFAVerifyRequest(BaseModel):
    secret_key: str
    totp_code: str


class MFAVerifyResponse(BaseModel):
    enabled: bool
    backup_codes: List[str]


class MFALoginRequest(BaseModel):
    totp_code: Optional[str] = None
    backup_code: Optional[str] = None


class DisableMFARequest(BaseModel):
    current_password: str


class ConsentRequest(BaseModel):
    consent_type: str
    granted: bool
    purpose: str


class AuditLogResponse(BaseModel):
    id: str
    action: str
    resource: Optional[str]
    timestamp: str
    ip_address: Optional[str]
    details: dict


class SecurityEventResponse(BaseModel):
    id: str
    event_type: str
    severity: str
    timestamp: str
    ip_address: Optional[str]
    resolved: bool


# MFA Endpoints
@router.post("/mfa/setup", response_model=MFASetupResponse)
@rate_limit("5/minute")
async def setup_mfa(
    request: Request,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """Setup MFA for the current user"""
    if current_user.mfa_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA is already enabled"
        )
    
    from ..services.auth_service import AuthService
    auth_service = AuthService(db)
    
    setup_data = auth_service.setup_mfa(current_user)
    return MFASetupResponse(**setup_data)


@router.post("/mfa/verify", response_model=MFAVerifyResponse)
@rate_limit("10/minute")
async def verify_mfa_setup(
    request: Request,
    request_data: MFAVerifyRequest,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """Verify and enable MFA for the current user"""
    from ..services.auth_service import AuthService
    auth_service = AuthService(db)
    
    result = auth_service.verify_mfa_setup(
        current_user,
        request_data.secret_key,
        request_data.totp_code
    )
    return MFAVerifyResponse(**result)


@router.post("/mfa/disable")
@rate_limit("3/minute")
async def disable_mfa(
    request: Request,
    request_data: DisableMFARequest,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """Disable MFA for the current user"""
    if not current_user.mfa_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA is not enabled"
        )
    
    from ..services.auth_service import AuthService
    auth_service = AuthService(db)
    
    success = auth_service.disable_mfa(current_user, request_data.current_password)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to disable MFA"
        )
    
    return {"message": "MFA disabled successfully"}


@router.post("/mfa/backup-codes")
@rate_limit("3/hour")
async def generate_backup_codes(
    request: Request,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """Generate new backup codes for MFA"""
    from ..services.auth_service import AuthService
    auth_service = AuthService(db)
    
    backup_codes = auth_service.generate_new_backup_codes(current_user)
    return {"backup_codes": backup_codes}


# Audit Log Endpoints
@router.get("/audit-logs", response_model=List[AuditLogResponse])
@rate_limit("30/minute")
async def get_user_audit_logs(
    request: Request,
    limit: int = 50,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """Get audit logs for the current user"""
    audit_service = AuditService(db)
    logs = audit_service.get_user_audit_trail(current_user.id, limit)
    
    return [
        AuditLogResponse(
            id=str(log.id),
            action=log.action,
            resource=log.resource,
            timestamp=log.timestamp.isoformat(),
            ip_address=log.ip_address,
            details=log.details or {}
        )
        for log in logs
    ]


# GDPR Compliance Endpoints
@router.post("/gdpr/consent")
@rate_limit("10/minute")
async def record_consent(
    request: Request,
    consent_data: ConsentRequest,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """Record user consent for data processing"""
    gdpr_service = GDPRService(db)
    
    # Get client IP for audit trail
    ip_address = request.client.host if request.client else None
    
    success = gdpr_service.record_consent(
        user=current_user,
        consent_type=consent_data.consent_type,
        granted=consent_data.granted,
        purpose=consent_data.purpose,
        ip_address=ip_address
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to record consent"
        )
    
    return {"message": "Consent recorded successfully"}


@router.post("/gdpr/withdraw-consent")
@rate_limit("10/minute")
async def withdraw_consent(
    request: Request,
    consent_type: str,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """Withdraw user consent"""
    gdpr_service = GDPRService(db)
    
    ip_address = request.client.host if request.client else None
    
    success = gdpr_service.withdraw_consent(
        user=current_user,
        consent_type=consent_type,
        ip_address=ip_address
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to withdraw consent"
        )
    
    return {"message": "Consent withdrawn successfully"}


@router.get("/gdpr/export-data")
@rate_limit("3/day")
async def export_user_data(
    request: Request,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """Export all user data (GDPR Article 20)"""
    gdpr_service = GDPRService(db)
    user_data = gdpr_service.export_user_data(current_user)
    
    return user_data


@router.get("/gdpr/download-data")
@rate_limit("3/day")
async def download_user_data(
    request: Request,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """Download user data as ZIP file"""
    gdpr_service = GDPRService(db)
    zip_data = gdpr_service.create_data_export_file(current_user)
    
    return Response(
        content=zip_data,
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename=user_data_{current_user.id}.zip"
        }
    )


@router.delete("/gdpr/delete-account")
@rate_limit("1/day")
async def delete_user_account(
    request: Request,
    hard_delete: bool = False,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """Delete user account (GDPR Article 17)"""
    gdpr_service = GDPRService(db)
    
    success = gdpr_service.delete_user_data(current_user, hard_delete)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete account"
        )
    
    return {"message": "Account deletion initiated"}


@router.get("/gdpr/privacy-dashboard")
@rate_limit("30/minute")
async def get_privacy_dashboard(
    request: Request,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """Get privacy dashboard data for user"""
    gdpr_service = GDPRService(db)
    dashboard_data = gdpr_service.get_privacy_dashboard_data(current_user)
    
    return dashboard_data


# Admin Security Endpoints (require admin role)
@router.get("/admin/security-events", response_model=List[SecurityEventResponse])
@rate_limit("60/minute")
async def get_security_events(
    request: Request,
    event_type: Optional[str] = None,
    resolved: Optional[bool] = None,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get security events (admin only)"""
    if current_user.user_type != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    audit_service = AuditService(db)
    events = audit_service.get_security_events(event_type, resolved, limit)
    
    return [
        SecurityEventResponse(
            id=str(event.id),
            event_type=event.event_type,
            severity=event.severity,
            timestamp=event.timestamp.isoformat(),
            ip_address=event.ip_address,
            resolved=event.resolved
        )
        for event in events
    ]


@router.get("/admin/security-dashboard")
@rate_limit("30/minute")
async def get_security_dashboard(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get security monitoring dashboard data (admin only)"""
    if current_user.user_type != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    security_monitoring = SecurityMonitoringService(db)
    dashboard_data = security_monitoring.get_security_dashboard_data()
    
    return dashboard_data


@router.post("/admin/resolve-security-event/{event_id}")
@rate_limit("30/minute")
async def resolve_security_event(
    request: Request,
    event_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Resolve a security event (admin only)"""
    if current_user.user_type != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    audit_service = AuditService(db)
    success = audit_service.resolve_security_event(event_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Security event not found"
        )
    
    return {"message": "Security event resolved"}