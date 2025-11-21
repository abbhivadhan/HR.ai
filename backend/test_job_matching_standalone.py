#!/usr/bin/env python3
"""
Standalone test for job matching functionality.
This bypasses the circular import issues by testing the core logic directly.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.job_matching_service import JobMatchingService
from app.models.profile import ExperienceLevel
from app.models.job import RemoteType
import uuid


def create_mock_candidate():
    """Create a mock candidate for testing."""
    class MockSkill:
        def __init__(self, name):
            self.name = name
    
    class MockCandidate:
        def __init__(self):
            self.skills = [
                MockSkill("Python"),
                MockSkill("JavaScript"),
                MockSkill("React"),
                MockSkill("Communication")
            ]
            self.experience_level = ExperienceLevel.MID
            self.experience_years = 3
            self.location = "San Francisco, CA"
            self.salary_min = 80000
            self.salary_max = 120000
            self.bio = "Experienced software engineer with expertise in Python and web development"
            self.current_title = "Software Engineer"
            self.experience = []
            self.user_id = str(uuid.uuid4())
    
    return MockCandidate()


def create_mock_job():
    """Create a mock job for testing."""
    class MockSkill:
        def __init__(self, name):
            self.name = name
    
    class MockJob:
        def __init__(self):
            self.required_skills = [
                MockSkill("Python"),
                MockSkill("JavaScript"),
                MockSkill("React"),
                MockSkill("Machine Learning")
            ]
            self.experience_level = ExperienceLevel.SENIOR
            self.location = "San Francisco, CA"
            self.remote_type = RemoteType.HYBRID
            self.salary_min = 100000
            self.salary_max = 150000
            self.title = "Senior Software Engineer"
            self.description = "We are looking for a senior software engineer with expertise in Python and web technologies"
            self.requirements = "5+ years of experience in software development"
            self.responsibilities = "Lead development of web applications"
            self.id = str(uuid.uuid4())
            self.company_id = str(uuid.uuid4())
    
    return MockJob()


def test_skill_matching():
    """Test skill matching functionality."""
    print("Testing skill matching...")
    
    matching_service = JobMatchingService(None)  # Mock db
    candidate = create_mock_candidate()
    job = create_mock_job()
    
    score = matching_service._calculate_skill_match_score(candidate, job)
    print(f"Skill match score: {score:.3f}")
    
    # Should have high score due to 3/4 skills matching
    assert score > 0.7, f"Expected skill score > 0.7, got {score}"
    assert score <= 1.0, f"Expected skill score <= 1.0, got {score}"
    print("✓ Skill matching test passed")


def test_experience_matching():
    """Test experience level matching."""
    print("Testing experience matching...")
    
    matching_service = JobMatchingService(None)
    candidate = create_mock_candidate()
    job = create_mock_job()
    
    # Test underqualified candidate (MID vs SENIOR)
    score = matching_service._calculate_experience_match_score(candidate, job)
    print(f"Experience match score (underqualified): {score:.3f}")
    assert 0.1 <= score < 1.0, f"Expected 0.1 <= score < 1.0, got {score}"
    
    # Test exact match
    candidate.experience_level = ExperienceLevel.SENIOR
    score = matching_service._calculate_experience_match_score(candidate, job)
    print(f"Experience match score (exact match): {score:.3f}")
    assert score == 1.0, f"Expected exact match score = 1.0, got {score}"
    
    print("✓ Experience matching test passed")


def test_location_matching():
    """Test location compatibility."""
    print("Testing location matching...")
    
    matching_service = JobMatchingService(None)
    candidate = create_mock_candidate()
    job = create_mock_job()
    
    # Test remote job
    job.remote_type = RemoteType.REMOTE
    score = matching_service._calculate_location_match_score(candidate, job)
    print(f"Location match score (remote): {score:.3f}")
    assert score == 1.0, f"Expected remote job score = 1.0, got {score}"
    
    # Test hybrid job
    job.remote_type = RemoteType.HYBRID
    score = matching_service._calculate_location_match_score(candidate, job)
    print(f"Location match score (hybrid): {score:.3f}")
    assert score == 0.8, f"Expected hybrid job score = 0.8, got {score}"
    
    # Test exact location match
    job.remote_type = RemoteType.ONSITE
    candidate.location = "San Francisco, CA"
    job.location = "San Francisco, CA"
    score = matching_service._calculate_location_match_score(candidate, job)
    print(f"Location match score (exact match): {score:.3f}")
    assert score == 1.0, f"Expected exact location match score = 1.0, got {score}"
    
    print("✓ Location matching test passed")


def test_salary_matching():
    """Test salary compatibility."""
    print("Testing salary matching...")
    
    matching_service = JobMatchingService(None)
    candidate = create_mock_candidate()
    job = create_mock_job()
    
    # Test overlapping ranges
    candidate.salary_min = 90000
    candidate.salary_max = 130000
    job.salary_min = 100000
    job.salary_max = 150000
    score = matching_service._calculate_salary_match_score(candidate, job)
    print(f"Salary match score (overlapping): {score:.3f}")
    assert score > 0.5, f"Expected overlapping salary score > 0.5, got {score}"
    
    # Test candidate expects less (good for employer)
    candidate.salary_min = 70000
    candidate.salary_max = 90000
    score = matching_service._calculate_salary_match_score(candidate, job)
    print(f"Salary match score (candidate expects less): {score:.3f}")
    assert score > 0.2, f"Expected score > 0.2 when candidate expects less, got {score}"
    
    print("✓ Salary matching test passed")


def test_content_based_filtering():
    """Test content-based filtering using TF-IDF."""
    print("Testing content-based filtering...")
    
    matching_service = JobMatchingService(None)
    candidate = create_mock_candidate()
    job = create_mock_job()
    
    # Mock text preparation methods for testing
    def mock_prepare_candidate_text(candidate):
        return "software engineer python javascript react web development"
    
    def mock_prepare_job_text(job):
        return "senior software engineer python web technologies development applications"
    
    matching_service._prepare_candidate_text = mock_prepare_candidate_text
    matching_service._prepare_job_text = mock_prepare_job_text
    
    score = matching_service._calculate_content_based_score(candidate, job)
    print(f"Content-based score: {score:.3f}")
    
    # Should have reasonable similarity due to overlapping terms
    assert 0.0 <= score <= 1.0, f"Expected 0.0 <= score <= 1.0, got {score}"
    assert score > 0.1, f"Expected some similarity, got {score}"
    
    print("✓ Content-based filtering test passed")


def test_hybrid_matching():
    """Test the complete hybrid matching algorithm."""
    print("Testing hybrid matching algorithm...")
    
    matching_service = JobMatchingService(None)
    candidate = create_mock_candidate()
    job = create_mock_job()
    
    # Mock methods to avoid database dependencies
    matching_service._find_similar_candidates = lambda c, limit: []
    matching_service._prepare_candidate_text = lambda c: "python software engineer developer"
    matching_service._prepare_job_text = lambda j: "python software engineer position"
    
    match_score = matching_service._calculate_hybrid_match_score(candidate, job)
    
    print(f"Overall match score: {match_score.overall_score:.3f}")
    print(f"Skill match score: {match_score.skill_match_score:.3f}")
    print(f"Experience match score: {match_score.experience_match_score:.3f}")
    print(f"Location match score: {match_score.location_match_score:.3f}")
    print(f"Salary match score: {match_score.salary_match_score:.3f}")
    print(f"Confidence level: {match_score.confidence_level:.3f}")
    print(f"Match reasons: {match_score.match_reasons}")
    print(f"Improvement suggestions: {match_score.improvement_suggestions}")
    
    # Validate all scores are within bounds
    assert 0.0 <= match_score.overall_score <= 1.0
    assert 0.0 <= match_score.skill_match_score <= 1.0
    assert 0.0 <= match_score.experience_match_score <= 1.0
    assert 0.0 <= match_score.location_match_score <= 1.0
    assert 0.0 <= match_score.salary_match_score <= 1.0
    assert 0.0 <= match_score.confidence_level <= 1.0
    
    # Should have some match reasons and suggestions
    assert isinstance(match_score.match_reasons, list)
    assert isinstance(match_score.improvement_suggestions, list)
    
    print("✓ Hybrid matching test passed")


def test_consistency():
    """Test that matching algorithm produces consistent results."""
    print("Testing algorithm consistency...")
    
    matching_service = JobMatchingService(None)
    candidate = create_mock_candidate()
    job = create_mock_job()
    
    # Mock methods
    matching_service._find_similar_candidates = lambda c, limit: []
    matching_service._prepare_candidate_text = lambda c: "python software engineer developer"
    matching_service._prepare_job_text = lambda j: "python software engineer position"
    
    # Calculate score multiple times
    scores = []
    for _ in range(5):
        match_score = matching_service._calculate_hybrid_match_score(candidate, job)
        scores.append(match_score.overall_score)
    
    print(f"Consistency test scores: {[f'{s:.3f}' for s in scores]}")
    
    # Scores should be consistent (same input should produce same output)
    for score in scores[1:]:
        assert abs(score - scores[0]) < 0.01, f"Inconsistent scores: {scores}"
    
    print("✓ Consistency test passed")


def main():
    """Run all tests."""
    print("Running Job Matching System Tests")
    print("=" * 50)
    
    try:
        test_skill_matching()
        test_experience_matching()
        test_location_matching()
        test_salary_matching()
        test_content_based_filtering()
        test_hybrid_matching()
        test_consistency()
        
        print("\n" + "=" * 50)
        print("✅ All tests passed! Job matching system is working correctly.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())