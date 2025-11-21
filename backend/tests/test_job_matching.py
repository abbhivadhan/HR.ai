"""
Tests for Job Matching System

Tests for collaborative filtering, content-based filtering, hybrid recommendations,
and matching accuracy.
"""

import pytest
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid

from app.models.user import User, UserType
from app.models.profile import CandidateProfile, CompanyProfile, Skill, ExperienceLevel
from app.models.job import JobPosting, JobApplication, JobStatus, RemoteType
from app.models.job_matching import (
    JobMatchScore, JobRecommendation, CandidateJobInteraction,
    MatchingPreferences, InteractionType, NotificationFrequency
)
from app.services.job_matching_service import JobMatchingService, JobMatchingNotificationService
from app.database import get_db


class TestJobMatchingService:
    """Test the core job matching service functionality."""
    
    @pytest.fixture
    def db_session(self):
        """Create a test database session."""
        # This would typically use a test database
        # For now, we'll mock the database operations
        pass
    
    @pytest.fixture
    def sample_skills(self, db_session):
        """Create sample skills for testing."""
        skills = [
            Skill(name="Python", category="programming"),
            Skill(name="JavaScript", category="programming"),
            Skill(name="React", category="framework"),
            Skill(name="Machine Learning", category="ai"),
            Skill(name="Communication", category="soft_skills"),
            Skill(name="Leadership", category="soft_skills"),
            Skill(name="SQL", category="database"),
            Skill(name="Docker", category="tools")
        ]
        return skills
    
    @pytest.fixture
    def sample_candidate(self, db_session, sample_skills):
        """Create a sample candidate for testing."""
        user = User(
            email="candidate@test.com",
            password_hash="hashed_password",
            first_name="John",
            last_name="Doe",
            user_type=UserType.CANDIDATE,
            is_active=True,
            is_verified=True
        )
        
        profile = CandidateProfile(
            user=user,
            current_title="Software Engineer",
            experience_years=3,
            experience_level=ExperienceLevel.MID,
            location="San Francisco, CA",
            salary_min=80000,
            salary_max=120000,
            bio="Experienced software engineer with expertise in Python and web development",
            skills=sample_skills[:5]  # Python, JavaScript, React, ML, Communication
        )
        
        return profile
    
    @pytest.fixture
    def sample_company(self, db_session):
        """Create a sample company for testing."""
        user = User(
            email="company@test.com",
            password_hash="hashed_password",
            first_name="Tech",
            last_name="Corp",
            user_type=UserType.COMPANY,
            is_active=True,
            is_verified=True
        )
        
        profile = CompanyProfile(
            user=user,
            company_name="TechCorp Inc",
            industry="Technology",
            description="Leading technology company"
        )
        
        return profile
    
    @pytest.fixture
    def sample_job(self, db_session, sample_company, sample_skills):
        """Create a sample job posting for testing."""
        job = JobPosting(
            company=sample_company.user,
            title="Senior Software Engineer",
            description="We are looking for a senior software engineer with expertise in Python and web technologies",
            experience_level=ExperienceLevel.SENIOR,
            location="San Francisco, CA",
            remote_type=RemoteType.HYBRID,
            salary_min=100000,
            salary_max=150000,
            status=JobStatus.ACTIVE,
            requirements="5+ years of experience in software development",
            responsibilities="Lead development of web applications",
            required_skills=sample_skills[:4]  # Python, JavaScript, React, ML
        )
        
        return job
    
    def test_skill_match_score_calculation(self, sample_candidate, sample_job):
        """Test skill matching score calculation."""
        matching_service = JobMatchingService(None)  # Mock db for unit test
        
        # Mock the database queries
        sample_candidate.skills = [
            type('Skill', (), {'name': 'Python'}),
            type('Skill', (), {'name': 'JavaScript'}),
            type('Skill', (), {'name': 'React'}),
            type('Skill', (), {'name': 'Communication'})
        ]
        
        sample_job.required_skills = [
            type('Skill', (), {'name': 'Python'}),
            type('Skill', (), {'name': 'JavaScript'}),
            type('Skill', (), {'name': 'React'}),
            type('Skill', (), {'name': 'Machine Learning'})
        ]
        
        score = matching_service._calculate_skill_match_score(sample_candidate, sample_job)
        
        # Should have high score due to 3/4 skills matching
        assert score > 0.7
        assert score <= 1.0
    
    def test_experience_match_score_calculation(self, sample_candidate, sample_job):
        """Test experience level matching score calculation."""
        matching_service = JobMatchingService(None)
        
        # Test exact match
        sample_candidate.experience_level = ExperienceLevel.SENIOR
        sample_job.experience_level = ExperienceLevel.SENIOR
        score = matching_service._calculate_experience_match_score(sample_candidate, sample_job)
        assert score == 1.0
        
        # Test underqualified candidate
        sample_candidate.experience_level = ExperienceLevel.MID
        sample_job.experience_level = ExperienceLevel.SENIOR
        score = matching_service._calculate_experience_match_score(sample_candidate, sample_job)
        assert 0.1 <= score < 1.0
        
        # Test overqualified candidate
        sample_candidate.experience_level = ExperienceLevel.SENIOR
        sample_job.experience_level = ExperienceLevel.MID
        score = matching_service._calculate_experience_match_score(sample_candidate, sample_job)
        assert 0.3 <= score < 1.0
    
    def test_location_match_score_calculation(self, sample_candidate, sample_job):
        """Test location compatibility score calculation."""
        matching_service = JobMatchingService(None)
        
        # Test remote job (should get high score)
        sample_job.remote_type = RemoteType.REMOTE
        score = matching_service._calculate_location_match_score(sample_candidate, sample_job)
        assert score == 1.0
        
        # Test hybrid job
        sample_job.remote_type = RemoteType.HYBRID
        score = matching_service._calculate_location_match_score(sample_candidate, sample_job)
        assert score == 0.8
        
        # Test exact location match
        sample_job.remote_type = RemoteType.ONSITE
        sample_candidate.location = "San Francisco, CA"
        sample_job.location = "San Francisco, CA"
        score = matching_service._calculate_location_match_score(sample_candidate, sample_job)
        assert score == 1.0
        
        # Test no location match for onsite job
        sample_candidate.location = "New York, NY"
        sample_job.location = "San Francisco, CA"
        score = matching_service._calculate_location_match_score(sample_candidate, sample_job)
        assert score == 0.3
    
    def test_salary_match_score_calculation(self, sample_candidate, sample_job):
        """Test salary expectation compatibility score calculation."""
        matching_service = JobMatchingService(None)
        
        # Test overlapping ranges
        sample_candidate.salary_min = 90000
        sample_candidate.salary_max = 130000
        sample_job.salary_min = 100000
        sample_job.salary_max = 150000
        score = matching_service._calculate_salary_match_score(sample_candidate, sample_job)
        assert score > 0.5
        
        # Test candidate expects less (good for employer)
        sample_candidate.salary_min = 70000
        sample_candidate.salary_max = 90000
        sample_job.salary_min = 100000
        sample_job.salary_max = 150000
        score = matching_service._calculate_salary_match_score(sample_candidate, sample_job)
        assert score > 0.2
        
        # Test candidate expects more
        sample_candidate.salary_min = 160000
        sample_candidate.salary_max = 200000
        sample_job.salary_min = 100000
        sample_job.salary_max = 150000
        score = matching_service._calculate_salary_match_score(sample_candidate, sample_job)
        assert score >= 0.1
    
    def test_content_based_filtering(self, sample_candidate, sample_job):
        """Test content-based filtering using TF-IDF similarity."""
        matching_service = JobMatchingService(None)
        
        # Mock text preparation methods
        def mock_prepare_candidate_text(candidate):
            return "software engineer python javascript react web development"
        
        def mock_prepare_job_text(job):
            return "senior software engineer python web technologies development applications"
        
        matching_service._prepare_candidate_text = mock_prepare_candidate_text
        matching_service._prepare_job_text = mock_prepare_job_text
        
        score = matching_service._calculate_content_based_score(sample_candidate, sample_job)
        
        # Should have reasonable similarity due to overlapping terms
        assert 0.0 <= score <= 1.0
    
    def test_match_reasons_generation(self, sample_candidate, sample_job):
        """Test generation of human-readable match reasons."""
        matching_service = JobMatchingService(None)
        
        scores = {
            'skill': 0.8,
            'experience': 0.9,
            'location': 0.8,
            'salary': 0.7
        }
        
        # Mock skills for testing
        sample_candidate.skills = [type('Skill', (), {'name': 'Python'})]
        sample_job.required_skills = [type('Skill', (), {'name': 'Python'})]
        sample_job.experience_level = ExperienceLevel.SENIOR
        sample_job.remote_type = RemoteType.REMOTE
        
        reasons = matching_service._generate_match_reasons(sample_candidate, sample_job, scores)
        
        assert len(reasons) > 0
        assert any("skill" in reason.lower() for reason in reasons)
        assert any("experience" in reason.lower() for reason in reasons)
    
    def test_improvement_suggestions_generation(self, sample_candidate, sample_job):
        """Test generation of improvement suggestions."""
        matching_service = JobMatchingService(None)
        
        scores = {
            'skill': 0.4,  # Low skill match
            'experience': 0.3  # Low experience match
        }
        
        # Mock skills with gaps
        sample_candidate.skills = [type('Skill', (), {'name': 'Python'})]
        sample_job.required_skills = [
            type('Skill', (), {'name': 'Python'}),
            type('Skill', (), {'name': 'Machine Learning'}),
            type('Skill', (), {'name': 'Docker'})
        ]
        sample_candidate.experience_level = ExperienceLevel.JUNIOR
        sample_job.experience_level = ExperienceLevel.SENIOR
        
        suggestions = matching_service._generate_improvement_suggestions(sample_candidate, sample_job, scores)
        
        assert len(suggestions) > 0
        assert any("skill" in suggestion.lower() for suggestion in suggestions)


class TestJobMatchingNotificationService:
    """Test the job matching notification service."""
    
    def test_notify_new_job_matches(self):
        """Test notification of candidates about new job matches."""
        notification_service = JobMatchingNotificationService(None)
        
        # Mock the matching service
        def mock_get_candidate_recommendations(job_id, limit, min_score):
            # Return mock recommendations
            mock_candidate = type('CandidateProfile', (), {
                'user_id': str(uuid.uuid4()),
                'allow_contact': True
            })
            mock_score = type('MatchScore', (), {
                'overall_score': 0.8
            })
            return [(mock_candidate, mock_score)]
        
        notification_service.matching_service.get_candidate_recommendations = mock_get_candidate_recommendations
        
        # Mock notification sending
        notifications_sent = []
        def mock_send_notification(candidate, job_id, match_score):
            notifications_sent.append((candidate, job_id, match_score))
        
        notification_service._send_job_match_notification = mock_send_notification
        
        job_id = str(uuid.uuid4())
        result = notification_service.notify_new_job_matches(job_id)
        
        assert result == 1
        assert len(notifications_sent) == 1
    
    def test_notify_skill_improvement_matches(self):
        """Test notification of candidates about new matches after skill improvements."""
        notification_service = JobMatchingNotificationService(None)
        
        # Mock the matching service
        def mock_get_job_recommendations(candidate_id, limit, min_score):
            mock_job = type('JobPosting', (), {'id': str(uuid.uuid4())})
            mock_score = type('MatchScore', (), {'overall_score': 0.85})
            mock_rec = type('JobRecommendation', (), {
                'job_posting': mock_job,
                'match_score': mock_score,
                'recommended_at': datetime.utcnow()
            })
            return [mock_rec]
        
        notification_service.matching_service.get_job_recommendations = mock_get_job_recommendations
        
        # Mock notification sending
        notifications_sent = []
        def mock_send_skill_notification(candidate_id, matches):
            notifications_sent.append((candidate_id, matches))
        
        notification_service._send_skill_improvement_notification = mock_send_skill_notification
        
        candidate_id = str(uuid.uuid4())
        result = notification_service.notify_skill_improvement_matches(candidate_id)
        
        assert result == 1
        assert len(notifications_sent) == 1


class TestJobMatchingAccuracy:
    """Test the accuracy and performance of matching algorithms."""
    
    def test_matching_algorithm_consistency(self):
        """Test that matching algorithm produces consistent results."""
        matching_service = JobMatchingService(None)
        
        # Create mock candidate and job
        candidate = type('CandidateProfile', (), {
            'skills': [type('Skill', (), {'name': 'Python'})],
            'experience_level': ExperienceLevel.MID,
            'experience_years': 3,
            'location': 'San Francisco, CA',
            'salary_min': 80000,
            'salary_max': 120000,
            'bio': 'Software engineer',
            'current_title': 'Developer',
            'experience': [],
            'user_id': str(uuid.uuid4())
        })
        
        job = type('JobPosting', (), {
            'required_skills': [type('Skill', (), {'name': 'Python'})],
            'experience_level': ExperienceLevel.MID,
            'location': 'San Francisco, CA',
            'remote_type': RemoteType.HYBRID,
            'salary_min': 90000,
            'salary_max': 130000,
            'title': 'Software Engineer',
            'description': 'Python developer position',
            'requirements': 'Python experience required',
            'responsibilities': 'Develop software',
            'id': str(uuid.uuid4()),
            'company_id': str(uuid.uuid4())
        })
        
        # Mock database methods
        matching_service._find_similar_candidates = lambda c, limit: []
        matching_service._prepare_candidate_text = lambda c: "python software engineer developer"
        matching_service._prepare_job_text = lambda j: "python software engineer position"
        
        # Calculate score multiple times
        scores = []
        for _ in range(5):
            match_score = matching_service._calculate_hybrid_match_score(candidate, job)
            scores.append(match_score.overall_score)
        
        # Scores should be consistent (same input should produce same output)
        assert all(abs(score - scores[0]) < 0.01 for score in scores)
    
    def test_score_boundaries(self):
        """Test that all scores are within valid boundaries."""
        matching_service = JobMatchingService(None)
        
        # Test with various candidate-job combinations
        test_cases = [
            # Perfect match case
            {
                'candidate_skills': ['Python', 'JavaScript'],
                'job_skills': ['Python', 'JavaScript'],
                'candidate_exp': ExperienceLevel.SENIOR,
                'job_exp': ExperienceLevel.SENIOR
            },
            # No match case
            {
                'candidate_skills': ['Java'],
                'job_skills': ['Python'],
                'candidate_exp': ExperienceLevel.JUNIOR,
                'job_exp': ExperienceLevel.EXECUTIVE
            },
            # Partial match case
            {
                'candidate_skills': ['Python', 'React'],
                'job_skills': ['Python', 'Angular'],
                'candidate_exp': ExperienceLevel.MID,
                'job_exp': ExperienceLevel.SENIOR
            }
        ]
        
        for case in test_cases:
            candidate = type('CandidateProfile', (), {
                'skills': [type('Skill', (), {'name': skill}) for skill in case['candidate_skills']],
                'experience_level': case['candidate_exp'],
                'experience_years': 3,
                'location': 'San Francisco, CA',
                'salary_min': 80000,
                'salary_max': 120000,
                'bio': 'Test candidate',
                'current_title': 'Developer',
                'experience': [],
                'user_id': str(uuid.uuid4())
            })
            
            job = type('JobPosting', (), {
                'required_skills': [type('Skill', (), {'name': skill}) for skill in case['job_skills']],
                'experience_level': case['job_exp'],
                'location': 'San Francisco, CA',
                'remote_type': RemoteType.HYBRID,
                'salary_min': 90000,
                'salary_max': 130000,
                'title': 'Test Job',
                'description': 'Test job description',
                'requirements': 'Test requirements',
                'responsibilities': 'Test responsibilities',
                'id': str(uuid.uuid4()),
                'company_id': str(uuid.uuid4())
            })
            
            # Mock methods
            matching_service._find_similar_candidates = lambda c, limit: []
            matching_service._prepare_candidate_text = lambda c: ' '.join(case['candidate_skills'])
            matching_service._prepare_job_text = lambda j: ' '.join(case['job_skills'])
            
            match_score = matching_service._calculate_hybrid_match_score(candidate, job)
            
            # All scores should be between 0 and 1
            assert 0.0 <= match_score.overall_score <= 1.0
            assert 0.0 <= match_score.skill_match_score <= 1.0
            assert 0.0 <= match_score.experience_match_score <= 1.0
            assert 0.0 <= match_score.location_match_score <= 1.0
            assert 0.0 <= match_score.salary_match_score <= 1.0
            assert 0.0 <= match_score.confidence_level <= 1.0


if __name__ == "__main__":
    pytest.main([__file__])