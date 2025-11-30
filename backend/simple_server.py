from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import Optional
from jose import jwt
from datetime import datetime, timedelta
import hashlib
import secrets
import os

app = FastAPI(title="Simple AI-HR Platform API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory user storage for testing
users_db = {}

# OAuth state storage (in production, use Redis or similar)
oauth_states = {}

SECRET_KEY = "test-secret-key"
ALGORITHM = "HS256"

# Google OAuth configuration (set these as environment variables)
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/api/auth/google/callback")

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    firstName: str
    lastName: str
    userType: str

class GoogleAuthRequest(BaseModel):
    email: str
    firstName: str
    lastName: str
    googleId: str
    userType: Optional[str] = "CANDIDATE"

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@app.get("/")
async def root():
    return {"message": "Simple AI-HR Platform API is running"}

@app.post("/api/auth/login", response_model=TokenResponse)
async def login(login_data: LoginRequest):
    """Simple login endpoint"""
    user = users_db.get(login_data.email)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Check password
    password_hash = hashlib.sha256(login_data.password.encode()).hexdigest()
    if password_hash != user["password_hash"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Create tokens
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    refresh_token = create_access_token(
        data={"sub": user["email"], "type": "refresh"}, 
        expires_delta=timedelta(days=7)
    )
    
    # Return user data without password
    user_data = {k: v for k, v in user.items() if k != "password_hash"}
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=user_data
    )

@app.post("/api/auth/register")
async def register(register_data: RegisterRequest):
    """Simple register endpoint"""
    if register_data.email in users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    user_id = str(len(users_db) + 1)
    password_hash = hashlib.sha256(register_data.password.encode()).hexdigest()
    
    new_user = {
        "id": user_id,
        "email": register_data.email,
        "password_hash": password_hash,
        "firstName": register_data.firstName,
        "lastName": register_data.lastName,
        "userType": register_data.userType.upper(),  # Ensure uppercase
        "isVerified": True  # Auto-verify for testing
    }
    
    users_db[register_data.email] = new_user
    
    # Return user data without password
    user_data = {k: v for k, v in new_user.items() if k != "password_hash"}
    
    return {"user": user_data}

@app.post("/api/auth/google", response_model=TokenResponse)
async def google_auth(google_data: GoogleAuthRequest):
    """
    Simple Google OAuth endpoint - accepts Google user data from frontend
    In production, this would verify the Google token
    """
    # Check if user exists
    user = users_db.get(google_data.email)
    
    if not user:
        # Create new user from Google data
        user_id = str(len(users_db) + 1)
        user = {
            "id": user_id,
            "email": google_data.email,
            "firstName": google_data.firstName,
            "lastName": google_data.lastName,
            "userType": google_data.userType.upper(),
            "isVerified": True,  # Google accounts are pre-verified
            "oauthProvider": "google",
            "oauthProviderId": google_data.googleId
        }
        users_db[google_data.email] = user
    
    # Create tokens
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    refresh_token = create_access_token(
        data={"sub": user["email"], "type": "refresh"}, 
        expires_delta=timedelta(days=7)
    )
    
    # Return user data
    user_data = {k: v for k, v in user.items() if k != "password_hash"}
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=user_data
    )

@app.get("/api/auth/google/url")
async def get_google_auth_url():
    """
    Generate Google OAuth URL
    For testing, this returns a mock URL
    """
    state = secrets.token_urlsafe(32)
    oauth_states[state] = {"created_at": datetime.utcnow()}
    
    # In production, this would be the real Google OAuth URL
    google_auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={GOOGLE_CLIENT_ID}&"
        f"redirect_uri={GOOGLE_REDIRECT_URI}&"
        f"response_type=code&"
        f"scope=openid%20email%20profile&"
        f"state={state}"
    )
    
    return {"url": google_auth_url, "state": state}

@app.get("/api/users/profile")
async def get_profile():
    """Simple profile endpoint"""
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required"
    )

@app.get("/api/users")
async def list_users():
    """List all users (for testing only)"""
    return {
        "users": [
            {k: v for k, v in user.items() if k != "password_hash"}
            for user in users_db.values()
        ]
    }

# Dashboard endpoints
@app.get("/api/dashboard/company/analytics")
async def get_company_analytics():
    """Get company dashboard analytics (demo data)"""
    return {
        "job_postings": {
            "total": 8,
            "active": 5,
            "filled": 2,
            "expired": 1
        },
        "applications": {
            "total": 156,
            "pending": 23,
            "reviewed": 45,
            "shortlisted": 18,
            "hired": 12
        },
        "candidates": {
            "total_viewed": 1250,
            "average_score": 78.5,
            "top_skills": ["JavaScript", "React", "Python", "Node.js", "AWS"]
        },
        "performance": {
            "average_time_to_hire": 21,
            "application_rate": 15.6,
            "interview_to_hire_ratio": 0.38
        }
    }

@app.get("/api/dashboard/candidate-insights")
async def get_candidate_insights():
    """Get candidate insights (demo data)"""
    return {
        "total_candidates": 1250,
        "active_candidates": 890,
        "top_skills": ["JavaScript", "React", "Python", "Node.js", "AWS"],
        "average_experience": 5.2,
        "skill_distribution": [
            {"skill": "JavaScript", "count": 450, "percentage": 36},
            {"skill": "React", "count": 380, "percentage": 30},
            {"skill": "Python", "count": 320, "percentage": 26},
            {"skill": "Node.js", "count": 290, "percentage": 23},
            {"skill": "AWS", "count": 250, "percentage": 20}
        ]
    }

if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("Simple AI-HR Platform API Server")
    print("=" * 60)
    print("Server running at: http://localhost:8000")
    print("API Docs: http://localhost:8000/docs")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8000)