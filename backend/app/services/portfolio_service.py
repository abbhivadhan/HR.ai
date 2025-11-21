"""Portfolio and Video Resume Service"""
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import boto3
from backend.app.models.portfolio import Portfolio, PortfolioProject, Achievement
from backend.app.config import settings


class PortfolioService:
    """Portfolio management service"""
    
    def __init__(self):
        self.s3_client = None
        if hasattr(settings, 'AWS_ACCESS_KEY_ID'):
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION
            )
        self.bucket_name = getattr(settings, 'S3_BUCKET_NAME', 'aihr-portfolios')
    
    def get_or_create_portfolio(
        self,
        db: Session,
        user_id: int
    ) -> Portfolio:
        """Get or create user portfolio"""
        portfolio = db.query(Portfolio).filter(
            Portfolio.user_id == user_id
        ).first()
        
        if not portfolio:
            portfolio = Portfolio(user_id=user_id)
            db.add(portfolio)
            db.commit()
            db.refresh(portfolio)
        
        return portfolio
    
    def update_portfolio(
        self,
        db: Session,
        portfolio_id: int,
        updates: Dict[str, Any]
    ) -> Portfolio:
        """Update portfolio"""
        portfolio = db.query(Portfolio).filter(
            Portfolio.id == portfolio_id
        ).first()
        
        if not portfolio:
            raise ValueError("Portfolio not found")
        
        for key, value in updates.items():
            if hasattr(portfolio, key):
                setattr(portfolio, key, value)
        
        portfolio.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(portfolio)
        
        return portfolio
    
    def add_project(
        self,
        db: Session,
        portfolio_id: int,
        project_data: Dict[str, Any]
    ) -> PortfolioProject:
        """Add project to portfolio"""
        project = PortfolioProject(
            portfolio_id=portfolio_id,
            **project_data
        )
        
        db.add(project)
        db.commit()
        db.refresh(project)
        
        return project
    
    def add_achievement(
        self,
        db: Session,
        portfolio_id: int,
        achievement_data: Dict[str, Any]
    ) -> Achievement:
        """Add achievement/badge to portfolio"""
        achievement = Achievement(
            portfolio_id=portfolio_id,
            **achievement_data
        )
        
        db.add(achievement)
        db.commit()
        db.refresh(achievement)
        
        return achievement
    
    def increment_view_count(
        self,
        db: Session,
        portfolio_id: int
    ):
        """Increment portfolio view count"""
        portfolio = db.query(Portfolio).filter(
            Portfolio.id == portfolio_id
        ).first()
        
        if portfolio:
            portfolio.view_count += 1
            db.commit()
    
    def generate_video_upload_url(
        self,
        user_id: int,
        file_name: str,
        content_type: str = "video/mp4"
    ) -> Dict[str, Any]:
        """Generate presigned URL for video upload"""
        if not self.s3_client:
            # Return mock URL for development
            return {
                "upload_url": f"https://mock-upload.example.com/{user_id}/{file_name}",
                "video_url": f"https://mock-cdn.example.com/{user_id}/{file_name}",
                "expires_in": 3600
            }
        
        key = f"videos/{user_id}/{file_name}"
        
        # Generate presigned POST URL
        upload_url = self.s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': self.bucket_name,
                'Key': key,
                'ContentType': content_type
            },
            ExpiresIn=3600
        )
        
        video_url = f"https://{self.bucket_name}.s3.amazonaws.com/{key}"
        
        return {
            "upload_url": upload_url,
            "video_url": video_url,
            "expires_in": 3600
        }
