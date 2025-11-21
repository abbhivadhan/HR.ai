"""
API Versioning System

Provides backward compatibility and version management for the AI-HR Platform API.
"""

from fastapi import Request, HTTPException, status
from typing import Dict, Any, Optional, Callable
from enum import Enum
import re
from datetime import datetime, timedelta


class APIVersion(str, Enum):
    """Supported API versions"""
    V1_0 = "1.0"
    V1_1 = "1.1"
    V2_0 = "2.0"  # Future version


class VersioningStrategy(str, Enum):
    """API versioning strategies"""
    HEADER = "header"
    URL_PATH = "url_path"
    QUERY_PARAM = "query_param"


class APIVersionManager:
    """Manages API versioning and backward compatibility"""
    
    def __init__(self):
        self.current_version = APIVersion.V1_1
        self.supported_versions = [APIVersion.V1_0, APIVersion.V1_1]
        self.deprecated_versions = []
        self.version_mappings = self._setup_version_mappings()
        self.deprecation_warnings = self._setup_deprecation_warnings()
    
    def _setup_version_mappings(self) -> Dict[str, Dict[str, Any]]:
        """Setup version-specific endpoint mappings"""
        return {
            APIVersion.V1_0: {
                "endpoints": {
                    "/api/auth/login": {
                        "response_transform": self._transform_v1_0_login_response,
                        "request_transform": None
                    },
                    "/api/assessments/start": {
                        "response_transform": self._transform_v1_0_assessment_response,
                        "request_transform": None
                    }
                },
                "deprecated_fields": [
                    "user.profile_picture_url",  # Renamed to avatar_url in v1.1
                    "assessment.difficulty"      # Changed to difficulty_level in v1.1
                ],
                "new_fields": []
            },
            APIVersion.V1_1: {
                "endpoints": {},
                "deprecated_fields": [],
                "new_fields": [
                    "user.avatar_url",
                    "assessment.difficulty_level",
                    "job.remote_work_options"
                ]
            }
        }
    
    def _setup_deprecation_warnings(self) -> Dict[str, Dict[str, Any]]:
        """Setup deprecation warnings for versions"""
        return {
            APIVersion.V1_0: {
                "sunset_date": "2024-12-31",
                "warning_message": "API v1.0 is deprecated and will be sunset on 2024-12-31. Please upgrade to v1.1 or later.",
                "migration_guide": "https://docs.aihr-platform.com/migration/v1.0-to-v1.1"
            }
        }
    
    def get_version_from_request(self, request: Request) -> str:
        """Extract API version from request"""
        
        # Try header first (preferred method)
        version = request.headers.get("API-Version")
        if version:
            return version
        
        # Try Accept header with version
        accept_header = request.headers.get("Accept", "")
        version_match = re.search(r"application/vnd\.aihr\.v(\d+\.\d+)\+json", accept_header)
        if version_match:
            return version_match.group(1)
        
        # Try query parameter
        version = request.query_params.get("version")
        if version:
            return version
        
        # Try URL path
        path = str(request.url.path)
        path_match = re.search(r"/api/v(\d+\.\d+)/", path)
        if path_match:
            return path_match.group(1)
        
        # Default to current version
        return self.current_version
    
    def validate_version(self, version: str) -> str:
        """Validate and normalize API version"""
        
        if version not in self.supported_versions:
            if version in self.deprecated_versions:
                raise HTTPException(
                    status_code=status.HTTP_410_GONE,
                    detail=f"API version {version} is no longer supported"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Unsupported API version: {version}. Supported versions: {', '.join(self.supported_versions)}"
                )
        
        return version
    
    def get_deprecation_warning(self, version: str) -> Optional[Dict[str, Any]]:
        """Get deprecation warning for version if applicable"""
        return self.deprecation_warnings.get(version)
    
    def transform_response(self, response_data: Dict[str, Any], version: str, endpoint: str) -> Dict[str, Any]:
        """Transform response data for backward compatibility"""
        
        if version == self.current_version:
            return response_data
        
        version_config = self.version_mappings.get(version, {})
        endpoint_config = version_config.get("endpoints", {}).get(endpoint, {})
        
        transform_func = endpoint_config.get("response_transform")
        if transform_func:
            return transform_func(response_data)
        
        # Apply general field transformations
        return self._apply_field_transformations(response_data, version)
    
    def transform_request(self, request_data: Dict[str, Any], version: str, endpoint: str) -> Dict[str, Any]:
        """Transform request data for forward compatibility"""
        
        if version == self.current_version:
            return request_data
        
        version_config = self.version_mappings.get(version, {})
        endpoint_config = version_config.get("endpoints", {}).get(endpoint, {})
        
        transform_func = endpoint_config.get("request_transform")
        if transform_func:
            return transform_func(request_data)
        
        return request_data
    
    def _apply_field_transformations(self, data: Dict[str, Any], version: str) -> Dict[str, Any]:
        """Apply general field transformations for version compatibility"""
        
        if version == APIVersion.V1_0:
            # Transform v1.1 fields back to v1.0 format
            if isinstance(data, dict):
                transformed = data.copy()
                
                # Handle user avatar_url -> profile_picture_url
                if "avatar_url" in transformed:
                    transformed["profile_picture_url"] = transformed.pop("avatar_url")
                
                # Handle assessment difficulty_level -> difficulty
                if "difficulty_level" in transformed:
                    transformed["difficulty"] = transformed.pop("difficulty_level")
                
                # Recursively transform nested objects
                for key, value in transformed.items():
                    if isinstance(value, dict):
                        transformed[key] = self._apply_field_transformations(value, version)
                    elif isinstance(value, list):
                        transformed[key] = [
                            self._apply_field_transformations(item, version) if isinstance(item, dict) else item
                            for item in value
                        ]
                
                return transformed
        
        return data
    
    def _transform_v1_0_login_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform login response for v1.0 compatibility"""
        
        # v1.0 didn't have refresh_token_expires_in field
        if "refresh_token_expires_in" in response_data:
            response_data.pop("refresh_token_expires_in")
        
        return response_data
    
    def _transform_v1_0_assessment_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform assessment response for v1.0 compatibility"""
        
        # v1.0 used different field names
        if "time_limit_minutes" in response_data:
            response_data["time_limit"] = response_data.pop("time_limit_minutes")
        
        if "total_questions" in response_data:
            response_data["question_count"] = response_data.pop("total_questions")
        
        return response_data


# Global version manager instance
version_manager = APIVersionManager()


def get_api_version(request: Request) -> str:
    """Dependency to get API version from request"""
    version = version_manager.get_version_from_request(request)
    return version_manager.validate_version(version)


def add_version_headers(response_data: Dict[str, Any], version: str) -> Dict[str, str]:
    """Add version-related headers to response"""
    
    headers = {
        "API-Version": version,
        "API-Supported-Versions": ", ".join(version_manager.supported_versions)
    }
    
    # Add deprecation warning if applicable
    deprecation_warning = version_manager.get_deprecation_warning(version)
    if deprecation_warning:
        headers["Deprecation"] = f"version={version}"
        headers["Sunset"] = deprecation_warning["sunset_date"]
        headers["Link"] = f'<{deprecation_warning["migration_guide"]}>; rel="successor-version"'
    
    return headers


class VersionedResponse:
    """Wrapper for versioned API responses"""
    
    def __init__(self, data: Dict[str, Any], version: str, endpoint: str):
        self.data = data
        self.version = version
        self.endpoint = endpoint
    
    def transform(self) -> Dict[str, Any]:
        """Transform response data based on version"""
        return version_manager.transform_response(self.data, self.version, self.endpoint)
    
    def get_headers(self) -> Dict[str, str]:
        """Get version-related headers"""
        return add_version_headers(self.data, self.version)


def create_versioned_endpoint(endpoint_func: Callable) -> Callable:
    """Decorator to create version-aware endpoints"""
    
    def wrapper(*args, **kwargs):
        request = kwargs.get("request")
        if request:
            version = get_api_version(request)
            kwargs["api_version"] = version
        
        return endpoint_func(*args, **kwargs)
    
    return wrapper