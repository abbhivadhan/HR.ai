"""
Integration Service - Connect with external platforms
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import httpx
import json

class IntegrationService:
    """Manage integrations with external platforms"""
    
    def __init__(self):
        self.integrations = {}
        self.api_keys = {}
    
    # LinkedIn Integration
    async def linkedin_post_job(
        self,
        job_data: Dict[str, Any],
        access_token: str
    ) -> Dict[str, Any]:
        """Post job to LinkedIn"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.linkedin.com/v2/jobs",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json"
                    },
                    json=self._format_linkedin_job(job_data)
                )
                return {
                    "success": True,
                    "job_id": response.json().get("id"),
                    "url": response.json().get("url")
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def linkedin_search_candidates(
        self,
        criteria: Dict[str, Any],
        access_token: str
    ) -> List[Dict[str, Any]]:
        """Search candidates on LinkedIn"""
        # Implementation for LinkedIn Recruiter API
        return []
    
    # Indeed Integration
    async def indeed_post_job(
        self,
        job_data: Dict[str, Any],
        api_key: str
    ) -> Dict[str, Any]:
        """Post job to Indeed"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.indeed.com/v1/jobs",
                    headers={"Authorization": f"Bearer {api_key}"},
                    json=self._format_indeed_job(job_data)
                )
                return {
                    "success": True,
                    "job_id": response.json().get("id")
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # Glassdoor Integration
    async def glassdoor_sync_company_profile(
        self,
        company_id: str,
        api_key: str
    ) -> Dict[str, Any]:
        """Sync company profile with Glassdoor"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://api.glassdoor.com/v1/companies/{company_id}",
                    headers={"Authorization": f"Bearer {api_key}"}
                )
                return {
                    "success": True,
                    "rating": response.json().get("rating"),
                    "reviews_count": response.json().get("reviews_count")
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # Slack Integration
    async def slack_send_notification(
        self,
        webhook_url: str,
        message: str,
        channel: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send notification to Slack"""
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "text": message,
                    "channel": channel
                }
                response = await client.post(webhook_url, json=payload)
                return {"success": response.status_code == 200}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def slack_notify_new_application(
        self,
        application_data: Dict[str, Any],
        webhook_url: str
    ) -> Dict[str, Any]:
        """Notify team about new application"""
        message = f"""
🎯 New Application Received!

*Candidate:* {application_data.get('candidate_name')}
*Position:* {application_data.get('job_title')}
*Match Score:* {application_data.get('match_score')}%
*Experience:* {application_data.get('experience_years')} years

<{application_data.get('application_url')}|View Application>
        """
        return await self.slack_send_notification(webhook_url, message)
    
    # Microsoft Teams Integration
    async def teams_send_notification(
        self,
        webhook_url: str,
        title: str,
        message: str,
        facts: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """Send notification to Microsoft Teams"""
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "@type": "MessageCard",
                    "@context": "https://schema.org/extensions",
                    "summary": title,
                    "themeColor": "0078D7",
                    "title": title,
                    "text": message,
                    "sections": [{"facts": facts}] if facts else []
                }
                response = await client.post(webhook_url, json=payload)
                return {"success": response.status_code == 200}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # Google Workspace Integration
    async def google_calendar_create_event(
        self,
        event_data: Dict[str, Any],
        access_token: str
    ) -> Dict[str, Any]:
        """Create event in Google Calendar"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://www.googleapis.com/calendar/v3/calendars/primary/events",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json"
                    },
                    json=self._format_google_calendar_event(event_data)
                )
                return {
                    "success": True,
                    "event_id": response.json().get("id"),
                    "link": response.json().get("htmlLink")
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def google_meet_create_meeting(
        self,
        meeting_data: Dict[str, Any],
        access_token: str
    ) -> Dict[str, Any]:
        """Create Google Meet meeting"""
        event_data = {
            **meeting_data,
            "conferenceData": {
                "createRequest": {
                    "requestId": f"meet-{datetime.now().timestamp()}",
                    "conferenceSolutionKey": {"type": "hangoutsMeet"}
                }
            }
        }
        return await self.google_calendar_create_event(event_data, access_token)
    
    # Zoom Integration
    async def zoom_create_meeting(
        self,
        meeting_data: Dict[str, Any],
        api_key: str,
        api_secret: str
    ) -> Dict[str, Any]:
        """Create Zoom meeting"""
        try:
            # Generate JWT token
            token = self._generate_zoom_jwt(api_key, api_secret)
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.zoom.us/v2/users/me/meetings",
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json"
                    },
                    json=self._format_zoom_meeting(meeting_data)
                )
                return {
                    "success": True,
                    "meeting_id": response.json().get("id"),
                    "join_url": response.json().get("join_url"),
                    "password": response.json().get("password")
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # Outlook Calendar Integration
    async def outlook_create_event(
        self,
        event_data: Dict[str, Any],
        access_token: str
    ) -> Dict[str, Any]:
        """Create event in Outlook Calendar"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://graph.microsoft.com/v1.0/me/events",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json"
                    },
                    json=self._format_outlook_event(event_data)
                )
                return {
                    "success": True,
                    "event_id": response.json().get("id"),
                    "link": response.json().get("webLink")
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # Background Check Integration
    async def checkr_initiate_background_check(
        self,
        candidate_data: Dict[str, Any],
        api_key: str
    ) -> Dict[str, Any]:
        """Initiate background check via Checkr"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.checkr.com/v1/candidates",
                    headers={"Authorization": f"Bearer {api_key}"},
                    json={
                        "first_name": candidate_data.get("first_name"),
                        "last_name": candidate_data.get("last_name"),
                        "email": candidate_data.get("email"),
                        "phone": candidate_data.get("phone"),
                        "dob": candidate_data.get("date_of_birth"),
                        "ssn": candidate_data.get("ssn")
                    }
                )
                return {
                    "success": True,
                    "candidate_id": response.json().get("id"),
                    "status": "pending"
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # DocuSign Integration
    async def docusign_send_offer_letter(
        self,
        offer_data: Dict[str, Any],
        api_key: str
    ) -> Dict[str, Any]:
        """Send offer letter via DocuSign"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://demo.docusign.net/restapi/v2.1/accounts/{accountId}/envelopes",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    },
                    json=self._format_docusign_envelope(offer_data)
                )
                return {
                    "success": True,
                    "envelope_id": response.json().get("envelopeId"),
                    "status": response.json().get("status")
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ATS Import/Export
    async def export_to_greenhouse(
        self,
        candidate_data: Dict[str, Any],
        api_key: str
    ) -> Dict[str, Any]:
        """Export candidate to Greenhouse ATS"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://harvest.greenhouse.io/v1/candidates",
                    headers={"Authorization": f"Basic {api_key}"},
                    json=self._format_greenhouse_candidate(candidate_data)
                )
                return {
                    "success": True,
                    "candidate_id": response.json().get("id")
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def import_from_lever(
        self,
        api_key: str,
        job_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Import candidates from Lever ATS"""
        try:
            async with httpx.AsyncClient() as client:
                url = "https://api.lever.co/v1/candidates"
                if job_id:
                    url += f"?posting_id={job_id}"
                
                response = await client.get(
                    url,
                    headers={"Authorization": f"Bearer {api_key}"}
                )
                return response.json().get("data", [])
        except Exception as e:
            return []
    
    # Helper methods for formatting
    def _format_linkedin_job(self, job_data: Dict) -> Dict:
        """Format job data for LinkedIn API"""
        return {
            "title": job_data.get("title"),
            "description": job_data.get("description"),
            "location": job_data.get("location"),
            "employmentType": job_data.get("employment_type"),
            "experienceLevel": job_data.get("experience_level")
        }
    
    def _format_indeed_job(self, job_data: Dict) -> Dict:
        """Format job data for Indeed API"""
        return {
            "title": job_data.get("title"),
            "description": job_data.get("description"),
            "location": job_data.get("location"),
            "jobType": job_data.get("job_type"),
            "salary": job_data.get("salary")
        }
    
    def _format_google_calendar_event(self, event_data: Dict) -> Dict:
        """Format event for Google Calendar"""
        return {
            "summary": event_data.get("title"),
            "description": event_data.get("description"),
            "start": {
                "dateTime": event_data.get("start_time"),
                "timeZone": event_data.get("timezone", "UTC")
            },
            "end": {
                "dateTime": event_data.get("end_time"),
                "timeZone": event_data.get("timezone", "UTC")
            },
            "attendees": [
                {"email": email} for email in event_data.get("attendees", [])
            ]
        }
    
    def _format_zoom_meeting(self, meeting_data: Dict) -> Dict:
        """Format meeting for Zoom"""
        return {
            "topic": meeting_data.get("title"),
            "type": 2,  # Scheduled meeting
            "start_time": meeting_data.get("start_time"),
            "duration": meeting_data.get("duration", 60),
            "timezone": meeting_data.get("timezone", "UTC"),
            "settings": {
                "host_video": True,
                "participant_video": True,
                "join_before_host": False,
                "mute_upon_entry": True,
                "waiting_room": True
            }
        }
    
    def _format_outlook_event(self, event_data: Dict) -> Dict:
        """Format event for Outlook"""
        return {
            "subject": event_data.get("title"),
            "body": {
                "contentType": "HTML",
                "content": event_data.get("description")
            },
            "start": {
                "dateTime": event_data.get("start_time"),
                "timeZone": event_data.get("timezone", "UTC")
            },
            "end": {
                "dateTime": event_data.get("end_time"),
                "timeZone": event_data.get("timezone", "UTC")
            },
            "attendees": [
                {
                    "emailAddress": {"address": email},
                    "type": "required"
                }
                for email in event_data.get("attendees", [])
            ]
        }
    
    def _format_docusign_envelope(self, offer_data: Dict) -> Dict:
        """Format envelope for DocuSign"""
        return {
            "emailSubject": "Job Offer - Please Sign",
            "documents": [{
                "documentBase64": offer_data.get("document_base64"),
                "name": "Offer Letter",
                "fileExtension": "pdf",
                "documentId": "1"
            }],
            "recipients": {
                "signers": [{
                    "email": offer_data.get("candidate_email"),
                    "name": offer_data.get("candidate_name"),
                    "recipientId": "1",
                    "routingOrder": "1"
                }]
            },
            "status": "sent"
        }
    
    def _format_greenhouse_candidate(self, candidate_data: Dict) -> Dict:
        """Format candidate for Greenhouse"""
        return {
            "first_name": candidate_data.get("first_name"),
            "last_name": candidate_data.get("last_name"),
            "email": candidate_data.get("email"),
            "phone": candidate_data.get("phone"),
            "resume": candidate_data.get("resume_url"),
            "applications": [{
                "job_id": candidate_data.get("job_id")
            }]
        }
    
    def _generate_zoom_jwt(self, api_key: str, api_secret: str) -> str:
        """Generate JWT token for Zoom API"""
        # Simplified - in production use proper JWT library
        return "mock_jwt_token"


# Global instance
integration_service = IntegrationService()
