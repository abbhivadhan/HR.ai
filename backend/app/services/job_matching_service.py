"""
Job Matching Service

Implements ML-powered job matching using collaborative filtering, content-based filtering,
and hybrid recommendation systems to match candidates with suitable job opportunities.
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional, Set
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
import json

from ..models.user import User, UserType
from ..models.profile import CandidateProfile, Skill, candidate_skills
from ..models.job import JobPosting, JobApplication, job_skills, JobStatus
from ..database import get_db

logger = logging.getLogger(__name__)


@dataclass
class MatchScore:
    """Represents a job-candidate match with detailed scoring"""
    job_id: str
    candidate_id: str
    overall_score: float
    skill_match_score: float
    experience_match_score: float
    location_match_score: float
    salary_match_score: float
    collaborative_score: float
    content_based_score: float
    confidence_level: float
    match_reasons: List[str]
    improvement_suggestions: List[str]


@dataclass
class JobRecommendation:
    """Job recommendation with match details"""
    job_posting: JobPosting
    match_score: MatchScore
    recommended_at: datetime


class JobMatchingService:
    """
    ML-powered job matching service implementing collaborative filtering,
    content-based filtering, and hybrid recommendation systems.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.skill_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.scaler = StandardScaler()
        
    def get_job_recommendations(
        self, 
        candidate_id: str, 
        limit: int = 10,
        min_score: float = 0.5
    ) -> List[JobRecommendation]:
        """
        Get personalized job recommendations for a candidate using hybrid approach.
        
        Args:
            candidate_id: UUID of the candidate
            limit: Maximum number of recommendations
            min_score: Minimum match score threshold
            
        Returns:
            List of job recommendations sorted by match score
        """
        try:
            # Get candidate profile
            candidate = self._get_candidate_profile(candidate_id)
            if not candidate:
                logger.warning(f"Candidate profile not found: {candidate_id}")
                return []
            
            # Get active job postings
            active_jobs = self._get_active_jobs()
            if not active_jobs:
                logger.info("No active jobs available for matching")
                return []
            
            # Calculate match scores for all jobs
            recommendations = []
            for job in active_jobs:
                # Skip jobs from companies the candidate already applied to recently
                if self._has_recent_application(candidate_id, job.id):
                    continue
                    
                match_score = self._calculate_hybrid_match_score(candidate, job)
                
                if match_score.overall_score >= min_score:
                    recommendation = JobRecommendation(
                        job_posting=job,
                        match_score=match_score,
                        recommended_at=datetime.utcnow()
                    )
                    recommendations.append(recommendation)
            
            # Sort by overall score and return top recommendations
            recommendations.sort(key=lambda x: x.match_score.overall_score, reverse=True)
            return recommendations[:limit]
            
        except Exception as e:
            logger.error(f"Error generating job recommendations: {str(e)}")
            return []
    
    def get_candidate_recommendations(
        self, 
        job_id: str, 
        limit: int = 20,
        min_score: float = 0.6
    ) -> List[Tuple[CandidateProfile, MatchScore]]:
        """
        Get recommended candidates for a job posting.
        
        Args:
            job_id: UUID of the job posting
            limit: Maximum number of candidate recommendations
            min_score: Minimum match score threshold
            
        Returns:
            List of (candidate, match_score) tuples sorted by match score
        """
        try:
            # Get job posting
            job = self.db.query(JobPosting).filter(JobPosting.id == job_id).first()
            if not job:
                logger.warning(f"Job posting not found: {job_id}")
                return []
            
            # Get available candidates (not already applied)
            applied_candidate_ids = self.db.query(JobApplication.candidate_id)\
                .filter(JobApplication.job_posting_id == job_id).subquery()
            
            candidates = self.db.query(CandidateProfile)\
                .join(User)\
                .filter(
                    User.user_type == UserType.CANDIDATE,
                    User.is_active == True,
                    CandidateProfile.profile_visibility.in_(['public', 'companies_only']),
                    ~CandidateProfile.user_id.in_(applied_candidate_ids)
                ).all()
            
            # Calculate match scores
            recommendations = []
            for candidate in candidates:
                match_score = self._calculate_hybrid_match_score(candidate, job)
                
                if match_score.overall_score >= min_score:
                    recommendations.append((candidate, match_score))
            
            # Sort by overall score
            recommendations.sort(key=lambda x: x[1].overall_score, reverse=True)
            return recommendations[:limit]
            
        except Exception as e:
            logger.error(f"Error generating candidate recommendations: {str(e)}")
            return []
    
    def _calculate_hybrid_match_score(
        self, 
        candidate: CandidateProfile, 
        job: JobPosting
    ) -> MatchScore:
        """
        Calculate hybrid match score combining collaborative and content-based filtering.
        """
        # Content-based scoring
        content_score = self._calculate_content_based_score(candidate, job)
        
        # Collaborative filtering score
        collaborative_score = self._calculate_collaborative_score(candidate, job)
        
        # Individual component scores
        skill_score = self._calculate_skill_match_score(candidate, job)
        experience_score = self._calculate_experience_match_score(candidate, job)
        location_score = self._calculate_location_match_score(candidate, job)
        salary_score = self._calculate_salary_match_score(candidate, job)
        
        # Weighted hybrid score
        weights = {
            'content': 0.4,
            'collaborative': 0.3,
            'skill': 0.15,
            'experience': 0.1,
            'location': 0.03,
            'salary': 0.02
        }
        
        overall_score = (
            weights['content'] * content_score +
            weights['collaborative'] * collaborative_score +
            weights['skill'] * skill_score +
            weights['experience'] * experience_score +
            weights['location'] * location_score +
            weights['salary'] * salary_score
        )
        
        # Calculate confidence level based on data availability
        confidence = self._calculate_confidence_level(candidate, job)
        
        # Generate match reasons and suggestions
        match_reasons = self._generate_match_reasons(candidate, job, {
            'skill': skill_score,
            'experience': experience_score,
            'location': location_score,
            'salary': salary_score
        })
        
        improvement_suggestions = self._generate_improvement_suggestions(candidate, job, {
            'skill': skill_score,
            'experience': experience_score
        })
        
        return MatchScore(
            job_id=str(job.id),
            candidate_id=str(candidate.user_id),
            overall_score=min(overall_score, 1.0),
            skill_match_score=skill_score,
            experience_match_score=experience_score,
            location_match_score=location_score,
            salary_match_score=salary_score,
            collaborative_score=collaborative_score,
            content_based_score=content_score,
            confidence_level=confidence,
            match_reasons=match_reasons,
            improvement_suggestions=improvement_suggestions
        )
    
    def _calculate_content_based_score(
        self, 
        candidate: CandidateProfile, 
        job: JobPosting
    ) -> float:
        """
        Calculate content-based similarity score using TF-IDF on job descriptions and candidate profiles.
        """
        try:
            # Prepare candidate text
            candidate_text = self._prepare_candidate_text(candidate)
            
            # Prepare job text
            job_text = self._prepare_job_text(job)
            
            if not candidate_text or not job_text:
                return 0.5  # Default score when text is insufficient
            
            # Calculate TF-IDF similarity
            documents = [candidate_text, job_text]
            tfidf_matrix = self.skill_vectorizer.fit_transform(documents)
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            return max(0.0, min(1.0, similarity))
            
        except Exception as e:
            logger.error(f"Error calculating content-based score: {str(e)}")
            return 0.5
    
    def _calculate_collaborative_score(
        self, 
        candidate: CandidateProfile, 
        job: JobPosting
    ) -> float:
        """
        Calculate collaborative filtering score based on similar candidates' application patterns.
        """
        try:
            # Find similar candidates based on skills and experience
            similar_candidates = self._find_similar_candidates(candidate, limit=50)
            
            if not similar_candidates:
                return 0.5  # Default score when no similar candidates found
            
            # Get application patterns of similar candidates
            similar_candidate_ids = [c.user_id for c in similar_candidates]
            
            # Find jobs that similar candidates applied to and were successful
            successful_applications = self.db.query(JobApplication)\
                .join(JobPosting)\
                .filter(
                    JobApplication.candidate_id.in_(similar_candidate_ids),
                    JobApplication.status.in_(['accepted', 'offered', 'shortlisted']),
                    JobPosting.company_id == job.company_id
                ).all()
            
            if not successful_applications:
                return 0.4  # Lower default when no successful patterns found
            
            # Calculate similarity to successful applications
            job_similarity_scores = []
            for app in successful_applications:
                job_sim = self._calculate_job_similarity(job, app.job_posting)
                job_similarity_scores.append(job_sim)
            
            # Return average similarity to successful applications
            return np.mean(job_similarity_scores) if job_similarity_scores else 0.4
            
        except Exception as e:
            logger.error(f"Error calculating collaborative score: {str(e)}")
            return 0.5
    
    def _calculate_skill_match_score(
        self, 
        candidate: CandidateProfile, 
        job: JobPosting
    ) -> float:
        """Calculate skill matching score between candidate and job requirements."""
        try:
            # Get candidate skills
            candidate_skills_set = set(skill.name.lower() for skill in candidate.skills)
            
            # Get required job skills
            job_skills_set = set(skill.name.lower() for skill in job.required_skills)
            
            if not job_skills_set:
                return 0.7  # Default score when job has no specified skills
            
            if not candidate_skills_set:
                return 0.2  # Low score when candidate has no skills listed
            
            # Calculate Jaccard similarity
            intersection = candidate_skills_set.intersection(job_skills_set)
            union = candidate_skills_set.union(job_skills_set)
            
            jaccard_score = len(intersection) / len(union) if union else 0
            
            # Boost score for having all required skills
            required_skills_match = len(intersection) / len(job_skills_set)
            
            # Weighted combination
            final_score = 0.6 * jaccard_score + 0.4 * required_skills_match
            
            return min(1.0, final_score)
            
        except Exception as e:
            logger.error(f"Error calculating skill match score: {str(e)}")
            return 0.5 
   
    def _calculate_experience_match_score(
        self, 
        candidate: CandidateProfile, 
        job: JobPosting
    ) -> float:
        """Calculate experience level matching score."""
        try:
            experience_levels = {
                'entry': 0,
                'junior': 1,
                'mid': 2,
                'senior': 3,
                'lead': 4,
                'executive': 5
            }
            
            candidate_level = experience_levels.get(candidate.experience_level, 0)
            required_level = experience_levels.get(job.experience_level, 0)
            
            # Perfect match gets 1.0
            if candidate_level == required_level:
                return 1.0
            
            # Calculate penalty for level mismatch
            level_diff = abs(candidate_level - required_level)
            
            # Overqualified candidates get slightly lower score
            if candidate_level > required_level:
                return max(0.3, 1.0 - (level_diff * 0.15))
            
            # Underqualified candidates get lower score
            else:
                return max(0.1, 1.0 - (level_diff * 0.25))
                
        except Exception as e:
            logger.error(f"Error calculating experience match score: {str(e)}")
            return 0.5
    
    def _calculate_location_match_score(
        self, 
        candidate: CandidateProfile, 
        job: JobPosting
    ) -> float:
        """Calculate location compatibility score."""
        try:
            # Remote jobs get high score
            if job.remote_type == 'remote':
                return 1.0
            
            # Hybrid jobs get good score
            if job.remote_type == 'hybrid':
                return 0.8
            
            # Check if candidate location matches job location
            if candidate.location and job.location:
                candidate_location = candidate.location.lower().strip()
                job_location = job.location.lower().strip()
                
                # Exact match
                if candidate_location == job_location:
                    return 1.0
                
                # Partial match (same city/state)
                if any(part in job_location for part in candidate_location.split(',')):
                    return 0.7
                
                # Check preferred locations
                if candidate.preferred_locations:
                    for pref_loc in candidate.preferred_locations:
                        if pref_loc.lower().strip() in job_location:
                            return 0.8
            
            # Default for onsite jobs with no location match
            return 0.3 if job.remote_type == 'onsite' else 0.6
            
        except Exception as e:
            logger.error(f"Error calculating location match score: {str(e)}")
            return 0.5
    
    def _calculate_salary_match_score(
        self, 
        candidate: CandidateProfile, 
        job: JobPosting
    ) -> float:
        """Calculate salary expectation compatibility score."""
        try:
            # If no salary info available, return neutral score
            if not all([candidate.salary_min, candidate.salary_max, job.salary_min, job.salary_max]):
                return 0.7
            
            candidate_min = candidate.salary_min
            candidate_max = candidate.salary_max
            job_min = job.salary_min
            job_max = job.salary_max
            
            # Check for overlap in salary ranges
            overlap_start = max(candidate_min, job_min)
            overlap_end = min(candidate_max, job_max)
            
            if overlap_start <= overlap_end:
                # Calculate overlap percentage
                candidate_range = candidate_max - candidate_min
                job_range = job_max - job_min
                overlap_size = overlap_end - overlap_start
                
                # Score based on overlap relative to both ranges
                candidate_overlap_pct = overlap_size / candidate_range if candidate_range > 0 else 1
                job_overlap_pct = overlap_size / job_range if job_range > 0 else 1
                
                return min(1.0, (candidate_overlap_pct + job_overlap_pct) / 2)
            
            # No overlap - check how close they are
            if candidate_max < job_min:
                # Candidate expects less than job offers (good for employer)
                gap = job_min - candidate_max
                return max(0.2, 1.0 - (gap / candidate_max))
            
            if candidate_min > job_max:
                # Candidate expects more than job offers
                gap = candidate_min - job_max
                return max(0.1, 1.0 - (gap / job_max))
            
            return 0.5
            
        except Exception as e:
            logger.error(f"Error calculating salary match score: {str(e)}")
            return 0.7
    
    def _calculate_confidence_level(
        self, 
        candidate: CandidateProfile, 
        job: JobPosting
    ) -> float:
        """Calculate confidence level based on data completeness."""
        confidence_factors = []
        
        # Candidate data completeness
        if candidate.skills:
            confidence_factors.append(0.3)
        if candidate.experience_years > 0:
            confidence_factors.append(0.2)
        if candidate.bio:
            confidence_factors.append(0.1)
        if candidate.experience:
            confidence_factors.append(0.2)
        
        # Job data completeness
        if job.required_skills:
            confidence_factors.append(0.1)
        if job.description:
            confidence_factors.append(0.05)
        if job.requirements:
            confidence_factors.append(0.05)
        
        return min(1.0, sum(confidence_factors))
    
    def _generate_match_reasons(
        self, 
        candidate: CandidateProfile, 
        job: JobPosting, 
        scores: Dict[str, float]
    ) -> List[str]:
        """Generate human-readable reasons for the match."""
        reasons = []
        
        # Skill matches
        if scores['skill'] > 0.7:
            matching_skills = set(s.name for s in candidate.skills) & set(s.name for s in job.required_skills)
            if matching_skills:
                reasons.append(f"Strong skill match: {', '.join(list(matching_skills)[:3])}")
        
        # Experience match
        if scores['experience'] > 0.8:
            reasons.append(f"Experience level aligns well with {job.experience_level} requirements")
        
        # Location compatibility
        if scores['location'] > 0.8:
            if job.remote_type == 'remote':
                reasons.append("Remote work opportunity matches preferences")
            else:
                reasons.append("Location is compatible with preferences")
        
        # Salary compatibility
        if scores['salary'] > 0.8:
            reasons.append("Salary range aligns with expectations")
        
        return reasons
    
    def _generate_improvement_suggestions(
        self, 
        candidate: CandidateProfile, 
        job: JobPosting, 
        scores: Dict[str, float]
    ) -> List[str]:
        """Generate suggestions for improving match score."""
        suggestions = []
        
        # Skill gaps
        if scores['skill'] < 0.6:
            candidate_skills = set(s.name for s in candidate.skills)
            required_skills = set(s.name for s in job.required_skills)
            missing_skills = required_skills - candidate_skills
            
            if missing_skills:
                suggestions.append(f"Consider developing skills in: {', '.join(list(missing_skills)[:3])}")
        
        # Experience gap
        if scores['experience'] < 0.5:
            experience_levels = ['entry', 'junior', 'mid', 'senior', 'lead', 'executive']
            current_idx = experience_levels.index(candidate.experience_level) if candidate.experience_level in experience_levels else 0
            required_idx = experience_levels.index(job.experience_level) if job.experience_level in experience_levels else 0
            
            if current_idx < required_idx:
                suggestions.append(f"Gain more experience to reach {job.experience_level} level")
        
        return suggestions
    
    def _find_similar_candidates(
        self, 
        candidate: CandidateProfile, 
        limit: int = 50
    ) -> List[CandidateProfile]:
        """Find candidates with similar profiles for collaborative filtering."""
        try:
            # Get candidates with similar skills
            candidate_skill_ids = [skill.id for skill in candidate.skills]
            
            if not candidate_skill_ids:
                return []
            
            # Find candidates with overlapping skills
            similar_candidates = self.db.query(CandidateProfile)\
                .join(candidate_skills)\
                .join(Skill)\
                .filter(
                    Skill.id.in_(candidate_skill_ids),
                    CandidateProfile.id != candidate.id,
                    CandidateProfile.experience_level == candidate.experience_level
                )\
                .group_by(CandidateProfile.id)\
                .having(func.count(Skill.id) >= max(1, len(candidate_skill_ids) // 3))\
                .limit(limit)\
                .all()
            
            return similar_candidates
            
        except Exception as e:
            logger.error(f"Error finding similar candidates: {str(e)}")
            return []
    
    def _calculate_job_similarity(self, job1: JobPosting, job2: JobPosting) -> float:
        """Calculate similarity between two job postings."""
        try:
            similarity_factors = []
            
            # Skill similarity
            job1_skills = set(s.name for s in job1.required_skills)
            job2_skills = set(s.name for s in job2.required_skills)
            
            if job1_skills and job2_skills:
                skill_similarity = len(job1_skills & job2_skills) / len(job1_skills | job2_skills)
                similarity_factors.append(skill_similarity * 0.4)
            
            # Experience level similarity
            if job1.experience_level == job2.experience_level:
                similarity_factors.append(0.3)
            
            # Company similarity (same company gets bonus)
            if job1.company_id == job2.company_id:
                similarity_factors.append(0.2)
            
            # Location similarity
            if job1.location and job2.location:
                if job1.location.lower() == job2.location.lower():
                    similarity_factors.append(0.1)
            
            return sum(similarity_factors)
            
        except Exception as e:
            logger.error(f"Error calculating job similarity: {str(e)}")
            return 0.0
    
    def _prepare_candidate_text(self, candidate: CandidateProfile) -> str:
        """Prepare candidate profile text for TF-IDF analysis."""
        text_parts = []
        
        if candidate.bio:
            text_parts.append(candidate.bio)
        
        if candidate.current_title:
            text_parts.append(candidate.current_title)
        
        # Add skills
        if candidate.skills:
            skills_text = ' '.join(skill.name for skill in candidate.skills)
            text_parts.append(skills_text)
        
        # Add work experience
        if candidate.experience:
            for exp in candidate.experience:
                if exp.description:
                    text_parts.append(exp.description)
                text_parts.append(f"{exp.position} {exp.company_name}")
        
        return ' '.join(text_parts)
    
    def _prepare_job_text(self, job: JobPosting) -> str:
        """Prepare job posting text for TF-IDF analysis."""
        text_parts = []
        
        text_parts.append(job.title)
        
        if job.description:
            text_parts.append(job.description)
        
        if job.requirements:
            text_parts.append(job.requirements)
        
        if job.responsibilities:
            text_parts.append(job.responsibilities)
        
        # Add required skills
        if job.required_skills:
            skills_text = ' '.join(skill.name for skill in job.required_skills)
            text_parts.append(skills_text)
        
        return ' '.join(text_parts)
    
    def _get_candidate_profile(self, candidate_id: str) -> Optional[CandidateProfile]:
        """Get candidate profile with related data."""
        return self.db.query(CandidateProfile)\
            .filter(CandidateProfile.user_id == candidate_id)\
            .first()
    
    def _get_active_jobs(self) -> List[JobPosting]:
        """Get all active job postings."""
        return self.db.query(JobPosting)\
            .filter(
                JobPosting.status == JobStatus.ACTIVE,
                or_(
                    JobPosting.expires_at.is_(None),
                    JobPosting.expires_at > datetime.utcnow()
                )
            )\
            .all()
    
    def _has_recent_application(self, candidate_id: str, job_id: str) -> bool:
        """Check if candidate has applied to this job recently."""
        recent_application = self.db.query(JobApplication)\
            .filter(
                JobApplication.candidate_id == candidate_id,
                JobApplication.job_posting_id == job_id,
                JobApplication.applied_at > datetime.utcnow() - timedelta(days=30)
            )\
            .first()
        
        return recent_application is not None
    
    def update_match_scores_for_candidate(self, candidate_id: str) -> None:
        """
        Update match scores for a candidate when their profile changes.
        This is called when candidate updates skills, experience, etc.
        """
        try:
            # Get active jobs
            active_jobs = self._get_active_jobs()
            candidate = self._get_candidate_profile(candidate_id)
            
            if not candidate:
                return
            
            # Recalculate scores for all active jobs
            updated_scores = []
            for job in active_jobs:
                match_score = self._calculate_hybrid_match_score(candidate, job)
                updated_scores.append(match_score)
            
            # Store updated scores (would typically update a match_scores table)
            logger.info(f"Updated match scores for candidate {candidate_id}: {len(updated_scores)} jobs processed")
            
        except Exception as e:
            logger.error(f"Error updating match scores for candidate {candidate_id}: {str(e)}")
    
    def get_match_analytics(self, job_id: str) -> Dict:
        """Get analytics for job matching performance."""
        try:
            job = self.db.query(JobPosting).filter(JobPosting.id == job_id).first()
            if not job:
                return {}
            
            # Get application statistics
            applications = self.db.query(JobApplication)\
                .filter(JobApplication.job_posting_id == job_id)\
                .all()
            
            total_applications = len(applications)
            successful_applications = len([app for app in applications 
                                         if app.status in ['accepted', 'offered']])
            
            # Calculate average match scores
            match_scores = [app.ai_match_score for app in applications if app.ai_match_score]
            avg_match_score = np.mean(match_scores) if match_scores else 0
            
            return {
                'job_id': str(job_id),
                'total_applications': total_applications,
                'successful_applications': successful_applications,
                'success_rate': successful_applications / total_applications if total_applications > 0 else 0,
                'average_match_score': avg_match_score,
                'match_score_distribution': {
                    'high': len([s for s in match_scores if s >= 0.8]),
                    'medium': len([s for s in match_scores if 0.6 <= s < 0.8]),
                    'low': len([s for s in match_scores if s < 0.6])
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting match analytics for job {job_id}: {str(e)}")
            return {}


class JobMatchingNotificationService:
    """
    Service for sending notifications about job matches and recommendations.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.matching_service = JobMatchingService(db)
    
    def notify_new_job_matches(self, job_id: str) -> int:
        """
        Notify candidates about new job that matches their profile.
        
        Args:
            job_id: UUID of the newly posted job
            
        Returns:
            Number of candidates notified
        """
        try:
            # Get candidate recommendations for this job
            recommendations = self.matching_service.get_candidate_recommendations(
                job_id, 
                limit=50, 
                min_score=0.7
            )
            
            notifications_sent = 0
            for candidate, match_score in recommendations:
                # Check if candidate allows notifications
                if candidate.allow_contact:
                    self._send_job_match_notification(candidate, job_id, match_score)
                    notifications_sent += 1
            
            logger.info(f"Sent {notifications_sent} job match notifications for job {job_id}")
            return notifications_sent
            
        except Exception as e:
            logger.error(f"Error sending job match notifications: {str(e)}")
            return 0
    
    def notify_skill_improvement_matches(self, candidate_id: str) -> int:
        """
        Notify candidate about new job matches after skill improvements.
        
        Args:
            candidate_id: UUID of the candidate
            
        Returns:
            Number of new matches found
        """
        try:
            # Get updated recommendations
            recommendations = self.matching_service.get_job_recommendations(
                candidate_id,
                limit=10,
                min_score=0.6
            )
            
            # Filter for high-quality matches
            high_quality_matches = [
                rec for rec in recommendations 
                if rec.match_score.overall_score >= 0.8
            ]
            
            if high_quality_matches:
                self._send_skill_improvement_notification(candidate_id, high_quality_matches)
                logger.info(f"Sent skill improvement notification to candidate {candidate_id} with {len(high_quality_matches)} matches")
            
            return len(high_quality_matches)
            
        except Exception as e:
            logger.error(f"Error sending skill improvement notifications: {str(e)}")
            return 0
    
    def _send_job_match_notification(
        self, 
        candidate: CandidateProfile, 
        job_id: str, 
        match_score: MatchScore
    ) -> None:
        """Send notification to candidate about job match."""
        # This would integrate with email/notification service
        # For now, just log the notification
        logger.info(f"Job match notification: Candidate {candidate.user_id} matched with job {job_id} (score: {match_score.overall_score:.2f})")
    
    def _send_skill_improvement_notification(
        self, 
        candidate_id: str, 
        matches: List[JobRecommendation]
    ) -> None:
        """Send notification about new matches after skill improvements."""
        # This would integrate with email/notification service
        logger.info(f"Skill improvement notification: Candidate {candidate_id} has {len(matches)} new high-quality matches")