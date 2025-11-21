from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas.auth import (
    UserRegistration,
    UserLogin,
    TokenResponse,
    UserResponse,
    PasswordResetRequest,
    PasswordReset,
    EmailVerification,
    RefreshTokenRequest
)
from ..services.auth_service import AuthService
from ..auth.dependencies import get_current_user, get_current_verified_user
from ..auth.utils import verify_token
from ..models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegistration,
    db: Session = Depends(get_db)
):
    """Register a new user."""
    auth_service = AuthService(db)
    user = auth_service.register_user(user_data)
    return UserResponse.from_orm(user)


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """Authenticate user and return tokens."""
    auth_service = AuthService(db)
    user = auth_service.authenticate_user(login_data)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    tokens = auth_service.create_tokens(user)
    return TokenResponse(**tokens)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token."""
    try:
        payload = verify_token(refresh_data.refresh_token)
        
        # Verify it's a refresh token
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
            
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
            
        auth_service = AuthService(db)
        user = auth_service.get_user_by_id(user_id)
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
            
        tokens = auth_service.create_tokens(user)
        return TokenResponse(**tokens)
        
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )


@router.post("/verify-email")
async def verify_email(
    verification_data: EmailVerification,
    db: Session = Depends(get_db)
):
    """Verify user email address."""
    auth_service = AuthService(db)
    success = auth_service.verify_email(verification_data.token)
    
    if success:
        return {"message": "Email verified successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token"
        )


@router.post("/forgot-password")
async def forgot_password(
    reset_request: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """Request password reset."""
    auth_service = AuthService(db)
    auth_service.request_password_reset(reset_request.email)
    
    return {"message": "If the email exists, a password reset link has been sent"}


@router.post("/reset-password")
async def reset_password(
    reset_data: PasswordReset,
    db: Session = Depends(get_db)
):
    """Reset password using reset token."""
    auth_service = AuthService(db)
    success = auth_service.reset_password(reset_data.token, reset_data.new_password)
    
    if success:
        return {"message": "Password reset successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information."""
    return UserResponse.from_orm(current_user)


@router.get("/me/verified", response_model=UserResponse)
async def get_current_verified_user_info(
    current_user: User = Depends(get_current_verified_user)
):
    """Get current verified user information."""
    return UserResponse.from_orm(current_user)