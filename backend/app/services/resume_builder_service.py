"""AI Resume Builder Service"""
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from openai import AsyncOpenAI
from backend.app.models.resume import Resume, ResumeExport, ATSOptimization
from backend.app.models.job import JobPosting
from backend.app.config import settings


class ResumeBuilderService:
    """AI-powered resume building service"""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4"
    
    async def create_resume(
        self,
        db: Session,
        user_id: int,
        title: str,
        template_id: str,
        content: Dict[str, Any]
    ) -> Resume:
        """Create a new resume"""
        resume = Resume(
            user_id=user_id,
            title=title,
            template_id=template_id,
            content=content
        )
        
        # Extract keywords
        resume.keywords = await self._extract_keywords(content)
        
        db.add(resume)
        db.commit()
        db.refresh(resume)
        
        return resume
    
    async def get_ai_suggestions(
        self,
        db: Session,
        resume_id: int,
        section: str
    ) -> List[Dict[str, Any]]:
        """Get AI content suggestions for resume section"""
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            raise ValueError("Resume not found")
        
        section_content = resume.content.get(section, {})
        
        prompt = f"""
        Improve this resume {section} section:
        
        {json.dumps(section_content, indent=2)}
        
        Provide 3-5 specific improvements with:
        - Original text
        - Suggested improvement
        - Reason for change
        - Impact level (high/medium/low)
        
        Focus on:
        - Action verbs
        - Quantifiable achievements
        - Industry keywords
        - Clear, concise language
        
        Return as JSON array.
        """
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        return result.get("suggestions", [])
    
    async def optimize_for_ats(
        self,
        db: Session,
        resume_id: int,
        job_id: Optional[int] = None,
        job_description: Optional[str] = None
    ) -> ATSOptimization:
        """Optimize resume for ATS"""
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            raise ValueError("Resume not found")
        
        # Get job description
        if job_id:
            job = db.query(JobPosting).filter(JobPosting.id == job_id).first()
            if job:
                job_description = job.description
        
        if not job_description:
            job_description = "General software engineering position"
        
        # Analyze ATS compatibility
        analysis = await self._analyze_ats_score(resume.content, job_description)
        
        optimization = ATSOptimization(
            resume_id=resume_id,
            job_id=job_id,
            score=analysis["score"],
            suggestions=analysis["suggestions"],
            missing_keywords=analysis["missing_keywords"],
            formatting_issues=analysis["formatting_issues"]
        )
        
        db.add(optimization)
        
        # Update resume ATS score
        resume.ats_score = analysis["score"]
        
        db.commit()
        db.refresh(optimization)
        
        return optimization
    
    async def _analyze_ats_score(
        self,
        resume_content: Dict[str, Any],
        job_description: str
    ) -> Dict[str, Any]:
        """Analyze ATS compatibility score"""
        prompt = f"""
        Analyze this resume for ATS (Applicant Tracking System) compatibility 
        against this job description.
        
        Resume:
        {json.dumps(resume_content, indent=2)}
        
        Job Description:
        {job_description}
        
        Provide:
        1. ATS score (0-100)
        2. Specific suggestions for improvement
        3. Missing keywords from job description
        4. Formatting issues
        
        Return as JSON with keys: score, suggestions, missing_keywords, formatting_issues
        """
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
    
    async def _extract_keywords(
        self,
        content: Dict[str, Any]
    ) -> List[str]:
        """Extract keywords from resume content"""
        prompt = f"""
        Extract 10-15 key skills and technologies from this resume:
        
        {json.dumps(content, indent=2)}
        
        Return as JSON array of strings.
        """
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        return result.get("keywords", [])
    
    async def export_resume(
        self,
        db: Session,
        resume_id: int,
        format: str
    ) -> ResumeExport:
        """Export resume to PDF/DOCX"""
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            raise ValueError("Resume not found")
        
        # TODO: Implement actual PDF/DOCX generation
        # For now, create placeholder
        file_url = f"https://storage.example.com/resumes/{resume_id}.{format}"
        
        export = ResumeExport(
            resume_id=resume_id,
            format=format,
            file_url=file_url,
            file_size=1024  # Placeholder
        )
        
        db.add(export)
        db.commit()
        db.refresh(export)
        
        return export
