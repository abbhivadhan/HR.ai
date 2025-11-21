"""
GDPR Compliance Service
Handles data protection and privacy compliance
"""
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text
from ..models.user import User
from ..models.security import AuditLog
from .audit_service import AuditService
from .encryption_service import encryption_service, field_encryption
import json
import zipfile
import io


class GDPRService:
    """Service for handling GDPR compliance requirements"""
    
    def __init__(self, db: Session):
        self.db = db
        self.audit_service = AuditService(db)
    
    def record_consent(
        self,
        user: User,
        consent_type: str,
        granted: bool,
        purpose: str,
        ip_address: Optional[str] = None
    ) -> bool:
        """Record user consent for data processing"""
        consent_data = {
            "consent_type": consent_type,
            "granted": granted,
            "purpose": purpose,
            "timestamp": datetime.utcnow().isoformat(),
            "ip_address": ip_address
        }
        
        # Store consent in user's audit trail
        self.audit_service.log_gdpr_action(
            user=user,
            action="CONSENT_RECORDED",
            request=None,
            details=consent_data
        )
        
        # Update user's consent preferences (this would be stored in a separate consent table in production)
        if not hasattr(user, 'gdpr_consents'):
            user.gdpr_consents = {}
        
        user.gdpr_consents = user.gdpr_consents or {}
        user.gdpr_consents[consent_type] = consent_data
        
        try:
            self.db.commit()
            return True
        except Exception:
            self.db.rollback()
            return False
    
    def withdraw_consent(self, user: User, consent_type: str, ip_address: Optional[str] = None) -> bool:
        """Allow user to withdraw consent"""
        withdrawal_data = {
            "consent_type": consent_type,
            "withdrawn": True,
            "timestamp": datetime.utcnow().isoformat(),
            "ip_address": ip_address
        }
        
        self.audit_service.log_gdpr_action(
            user=user,
            action="CONSENT_WITHDRAWN",
            request=None,
            details=withdrawal_data
        )
        
        # Update consent status
        if hasattr(user, 'gdpr_consents') and user.gdpr_consents:
            user.gdpr_consents[consent_type] = withdrawal_data
            
            try:
                self.db.commit()
                return True
            except Exception:
                self.db.rollback()
                return False
        
        return False
    
    def export_user_data(self, user: User) -> Dict[str, Any]:
        """Export all user data (Right to Data Portability - Article 20)"""
        self.audit_service.log_gdpr_action(
            user=user,
            action="DATA_EXPORT_REQUESTED",
            request=None,
            details={"export_timestamp": datetime.utcnow().isoformat()}
        )
        
        # Collect all user data from different tables
        user_data = {
            "personal_information": {
                "id": str(user.id),
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "user_type": user.user_type,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "updated_at": user.updated_at.isoformat() if user.updated_at else None,
                "last_login": user.last_login.isoformat() if user.last_login else None,
                "is_verified": user.is_verified,
                "mfa_enabled": user.mfa_enabled
            },
            "profile_data": {},
            "assessments": [],
            "job_applications": [],
            "audit_trail": [],
            "consent_history": getattr(user, 'gdpr_consents', {})
        }
        
        # Get profile data
        if user.candidate_profile:
            profile = user.candidate_profile
            user_data["profile_data"] = {
                "skills": [skill.name for skill in profile.skills] if hasattr(profile, 'skills') else [],
                "experience_years": getattr(profile, 'experience_years', None),
                "preferred_locations": getattr(profile, 'preferred_locations', []),
                "salary_expectation": getattr(profile, 'salary_expectation', None)
            }
        elif user.company_profile:
            profile = user.company_profile
            user_data["profile_data"] = {
                "company_name": getattr(profile, 'company_name', None),
                "industry": getattr(profile, 'industry', None),
                "company_size": getattr(profile, 'company_size', None),
                "website": getattr(profile, 'website', None)
            }
        
        # Get assessment data (anonymized scores only)
        # This would query the assessments table
        
        # Get job applications
        if hasattr(user, 'applications'):
            for application in user.applications:
                user_data["job_applications"].append({
                    "job_title": application.job_posting.title if application.job_posting else "Unknown",
                    "applied_at": application.created_at.isoformat() if application.created_at else None,
                    "status": getattr(application, 'status', 'Unknown')
                })
        
        # Get audit trail (last 100 entries)
        audit_logs = self.audit_service.get_user_audit_trail(user.id, limit=100)
        for log in audit_logs:
            user_data["audit_trail"].append({
                "action": log.action,
                "timestamp": log.timestamp.isoformat(),
                "ip_address": log.ip_address,
                "details": log.details
            })
        
        return user_data
    
    def create_data_export_file(self, user: User) -> bytes:
        """Create a downloadable file with user's data"""
        user_data = self.export_user_data(user)
        
        # Create a ZIP file with JSON data
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add main data file
            json_data = json.dumps(user_data, indent=2, default=str)
            zip_file.writestr("user_data.json", json_data)
            
            # Add GDPR information file
            gdpr_info = {
                "export_date": datetime.utcnow().isoformat(),
                "data_controller": "AI-HR Platform",
                "contact_email": "privacy@ai-hr-platform.com",
                "retention_policy": "Data is retained for 7 years after account deletion",
                "your_rights": [
                    "Right to access your data",
                    "Right to rectify incorrect data",
                    "Right to erase your data",
                    "Right to restrict processing",
                    "Right to data portability",
                    "Right to object to processing"
                ]
            }
            zip_file.writestr("gdpr_information.json", json.dumps(gdpr_info, indent=2))
        
        zip_buffer.seek(0)
        return zip_buffer.getvalue()
    
    def anonymize_user_data(self, user: User) -> bool:
        """Anonymize user data while preserving analytics (Right to be Forgotten - Article 17)"""
        self.audit_service.log_gdpr_action(
            user=user,
            action="DATA_ANONYMIZATION_REQUESTED",
            request=None,
            details={"anonymization_timestamp": datetime.utcnow().isoformat()}
        )
        
        try:
            # Generate anonymous identifier
            anonymous_id = f"anon_{user.id.hex[:8]}"
            
            # Anonymize personal data
            user.email = f"{anonymous_id}@anonymized.local"
            user.first_name = "Anonymous"
            user.last_name = "User"
            # Use a secure hash for anonymized password
            from ..auth.utils import get_password_hash
            user.password_hash = get_password_hash("ANONYMIZED_ACCOUNT")
            user.is_active = False
            user.is_verified = False
            user.verification_token = None
            user.reset_token = None
            user.mfa_secret = None
            user.mfa_backup_codes = None
            
            # Anonymize profile data
            if user.candidate_profile:
                profile = user.candidate_profile
                # Keep skills and experience for analytics but remove personal info
                if hasattr(profile, 'resume_url'):
                    profile.resume_url = None
                if hasattr(profile, 'phone_number'):
                    profile.phone_number = None
                if hasattr(profile, 'address'):
                    profile.address = None
            
            elif user.company_profile:
                profile = user.company_profile
                profile.company_name = f"Anonymous Company {anonymous_id}"
                if hasattr(profile, 'website'):
                    profile.website = None
                if hasattr(profile, 'contact_email'):
                    profile.contact_email = None
            
            # Keep assessment and application data for analytics but anonymize
            # This would involve updating related tables
            
            self.db.commit()
            
            self.audit_service.log_gdpr_action(
                user=user,
                action="DATA_ANONYMIZATION_COMPLETED",
                request=None,
                details={"anonymous_id": anonymous_id}
            )
            
            return True
            
        except Exception as e:
            self.db.rollback()
            self.audit_service.log_gdpr_action(
                user=user,
                action="DATA_ANONYMIZATION_FAILED",
                request=None,
                details={"error": str(e)}
            )
            return False
    
    def delete_user_data(self, user: User, hard_delete: bool = False) -> bool:
        """Delete user data (Right to Erasure - Article 17)"""
        self.audit_service.log_gdpr_action(
            user=user,
            action="DATA_DELETION_REQUESTED",
            request=None,
            details={
                "deletion_timestamp": datetime.utcnow().isoformat(),
                "hard_delete": hard_delete
            }
        )
        
        try:
            if hard_delete:
                # Complete deletion - removes all traces
                # Delete related data first (foreign key constraints)
                if user.candidate_profile:
                    self.db.delete(user.candidate_profile)
                if user.company_profile:
                    self.db.delete(user.company_profile)
                
                # Delete audit logs
                self.db.query(AuditLog).filter(AuditLog.user_id == user.id).delete()
                
                # Delete the user
                self.db.delete(user)
                
            else:
                # Soft delete - anonymize instead of complete removal
                return self.anonymize_user_data(user)
            
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            return False
    
    def get_data_retention_info(self) -> Dict[str, Any]:
        """Get information about data retention policies"""
        return {
            "retention_periods": {
                "user_accounts": "7 years after account deletion",
                "assessment_data": "5 years for analytics purposes",
                "audit_logs": "10 years for compliance",
                "job_applications": "3 years after application",
                "interview_recordings": "1 year after interview"
            },
            "legal_basis": {
                "user_data": "Contract performance and legitimate interest",
                "assessment_data": "Legitimate interest for service improvement",
                "audit_logs": "Legal obligation for security compliance"
            },
            "data_categories": {
                "personal_data": ["name", "email", "phone", "address"],
                "sensitive_data": ["assessment_results", "interview_recordings"],
                "technical_data": ["ip_address", "browser_info", "usage_analytics"]
            }
        }
    
    def check_consent_status(self, user: User, consent_type: str) -> Optional[Dict[str, Any]]:
        """Check current consent status for a user"""
        if hasattr(user, 'gdpr_consents') and user.gdpr_consents:
            return user.gdpr_consents.get(consent_type)
        return None
    
    def get_privacy_dashboard_data(self, user: User) -> Dict[str, Any]:
        """Get privacy dashboard data for user"""
        return {
            "data_summary": {
                "account_created": user.created_at.isoformat() if user.created_at else None,
                "last_login": user.last_login.isoformat() if user.last_login else None,
                "data_exports": self._count_user_exports(user),
                "consent_changes": self._count_consent_changes(user)
            },
            "current_consents": getattr(user, 'gdpr_consents', {}),
            "data_retention": self.get_data_retention_info(),
            "your_rights": [
                "Access your personal data",
                "Correct inaccurate data",
                "Delete your data",
                "Restrict data processing",
                "Data portability",
                "Object to processing",
                "Withdraw consent"
            ]
        }
    
    def _count_user_exports(self, user: User) -> int:
        """Count number of data exports for user"""
        return (
            self.db.query(AuditLog)
            .filter(
                AuditLog.user_id == user.id,
                AuditLog.action == "GDPR_DATA_EXPORT_REQUESTED"
            )
            .count()
        )
    
    def _count_consent_changes(self, user: User) -> int:
        """Count number of consent changes for user"""
        return (
            self.db.query(AuditLog)
            .filter(
                AuditLog.user_id == user.id,
                AuditLog.action.in_(["GDPR_CONSENT_RECORDED", "GDPR_CONSENT_WITHDRAWN"])
            )
            .count()
        )