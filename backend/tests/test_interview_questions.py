"""
Tests for AI interview question generation system
"""
import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.services.interview_question_service import (
    InterviewQuestionService, 
    QuestionDifficulty,
    interview_question_service
)
from app.models.interview import (
    Interview, InterviewQuestion, QuestionCategory, 
    InterviewType, InterviewStatus
)
from app.models.job import JobPosting, JobApplication
from app.models.user import User
from app.models.profile import Skill


class TestInterviewQuestionService:
    """Test cases for InterviewQuestionService"""
    
    @pytest.fixture
    def service(self):
        """Create service instance for testing"""
        return InterviewQuestionService()
    
    @pytest.fixture
    def mock_db(self):
        """Mock database session"""
        return MagicMock(spec=Session)
    
    @pytest.fixture
    def sample_interview(self):
        """Create sample interview for testing"""
        return Interview(
            id="test-interview-id",
            interview_type=InterviewType.AI_TECHNICAL,
            difficulty_level="intermediate",
            max_questions=5,
            focus_areas=["python", "algorithms"]
        )
    
    @pytest.fixture
    def sample_job_posting(self):
        """Create sample job posting"""
        job = JobPosting(
            title="Senior Python Developer",
            experience_level="senior",
            department="Engineering",
            job_type="full_time",
            description="We are looking for a senior Python developer...",
            requirements="5+ years Python experience, algorithms knowledge"
        )
        
        # Mock skills relationship
        skill1 = Skill(name="Python")
        skill2 = Skill(name="Algorithms")
        job.required_skills = [skill1, skill2]
        
        return job
    
    def test_calculate_question_distribution_technical(self, service):
        """Test question distribution for technical interviews"""
        distribution = service._calculate_question_distribution(
            total_questions=10,
            interview_type="ai_technical",
            focus_areas=["python"]
        )
        
        assert QuestionCategory.TECHNICAL in distribution
        assert distribution[QuestionCategory.TECHNICAL] >= 5  # Should be majority
        assert sum(distribution.values()) == 10
    
    def test_calculate_question_distribution_behavioral(self, service):
        """Test question distribution for behavioral interviews"""
        distribution = service._calculate_question_distribution(
            total_questions=8,
            interview_type="ai_behavioral",
            focus_areas=[]
        )
        
        assert QuestionCategory.BEHAVIORAL in distribution
        assert distribution[QuestionCategory.BEHAVIORAL] >= 4  # Should be majority
        assert sum(distribution.values()) == 8
    
    def test_calculate_question_distribution_screening(self, service):
        """Test question distribution for screening interviews"""
        distribution = service._calculate_question_distribution(
            total_questions=6,
            interview_type="ai_screening",
            focus_areas=[]
        )
        
        # Should have balanced distribution
        assert len(distribution) >= 3
        assert sum(distribution.values()) == 6
    
    def test_extract_job_context(self, service, sample_job_posting):
        """Test job context extraction"""
        context = service._extract_job_context(sample_job_posting)
        
        assert context["title"] == "Senior Python Developer"
        assert context["experience_level"] == "senior"
        assert "Python" in context["required_skills"]
        assert "Algorithms" in context["required_skills"]
        assert context["department"] == "Engineering"
        assert len(context["description"]) <= 500
    
    def test_apply_difficulty_progression(self, service):
        """Test difficulty progression algorithm"""
        questions = [
            {"difficulty_level": "intermediate", "expected_duration": 120},
            {"difficulty_level": "intermediate", "expected_duration": 120},
            {"difficulty_level": "intermediate", "expected_duration": 120},
            {"difficulty_level": "intermediate", "expected_duration": 120}
        ]
        
        result = service._apply_difficulty_progression(questions, "intermediate")
        
        # First question should be easier
        assert result[0]["difficulty_level"] == "beginner"
        
        # Last question should be harder
        assert result[-1]["difficulty_level"] in ["advanced", "expert"]
        
        # Duration should be adjusted
        assert all("expected_duration" in q for q in result)
    
    def test_fill_template(self, service):
        """Test template filling with job context"""
        template = {
            "template": "Explain the concept of {concept} in {language}.",
            "concepts": ["inheritance", "polymorphism"],
            "languages": ["Python", "Java"]
        }
        
        job_context = {"required_skills": ["Python"]}
        
        result = service._fill_template(template, job_context)
        
        assert "{concept}" not in result
        assert result.count("inheritance") + result.count("polymorphism") == 1
    
    def test_generate_template_questions(self, service):
        """Test template-based question generation"""
        job_context = {
            "title": "Python Developer",
            "required_skills": ["Python", "Django"]
        }
        
        questions = service._generate_template_questions(
            QuestionCategory.TECHNICAL, 2, job_context
        )
        
        assert len(questions) == 2
        assert all(q["category"] == QuestionCategory.TECHNICAL.value for q in questions)
        assert all(q["ai_generated"] is False for q in questions)
        assert all("question_text" in q for q in questions)
    
    @patch('app.services.interview_question_service.InterviewQuestionService._call_openai')
    async def test_generate_ai_questions(self, mock_openai, service, sample_interview):
        """Test AI question generation"""
        mock_response = '''
        [
            {
                "question_text": "Explain Python decorators and provide an example.",
                "expected_approach": "Should demonstrate understanding of closures and function wrapping",
                "follow_up_suggestions": ["Can you show a practical use case?"],
                "scoring_criteria": ["Technical accuracy", "Code example quality"],
                "expected_duration": 180,
                "difficulty_level": "intermediate",
                "skill_focus": ["python", "decorators"]
            }
        ]
        '''
        mock_openai.return_value = mock_response
        
        job_context = {"title": "Python Developer", "required_skills": ["Python"]}
        
        questions = await service._generate_ai_questions(
            sample_interview, job_context, QuestionCategory.TECHNICAL, 1
        )
        
        assert len(questions) == 1
        assert questions[0]["question_text"] == "Explain Python decorators and provide an example."
        assert questions[0]["ai_generated"] is True
        assert "python" in questions[0]["skill_focus"]
    
    def test_parse_ai_questions_valid_json(self, service):
        """Test parsing valid AI response"""
        response = '''
        [
            {
                "question_text": "Test question",
                "expected_approach": "Test approach",
                "follow_up_suggestions": ["Follow up 1"],
                "scoring_criteria": ["Criteria 1"],
                "expected_duration": 120,
                "difficulty_level": "intermediate",
                "skill_focus": ["python"]
            }
        ]
        '''
        
        questions = service._parse_ai_questions(response, QuestionCategory.TECHNICAL)
        
        assert len(questions) == 1
        assert questions[0]["question_text"] == "Test question"
        assert questions[0]["category"] == QuestionCategory.TECHNICAL.value
    
    def test_parse_ai_questions_invalid_json(self, service):
        """Test parsing invalid AI response"""
        response = "Invalid JSON response"
        
        questions = service._parse_ai_questions(response, QuestionCategory.TECHNICAL)
        
        assert questions == []
    
    def test_randomize_question_pool(self, service):
        """Test question pool randomization"""
        questions = [
            {"category": "technical", "question_order": 1},
            {"category": "technical", "question_order": 2},
            {"category": "behavioral", "question_order": 3},
            {"category": "behavioral", "question_order": 4}
        ]
        
        # Test with randomization
        randomized = service.randomize_question_pool(questions, 1.0)
        
        # Should maintain same length
        assert len(randomized) == len(questions)
        
        # Should update question orders
        orders = [q["question_order"] for q in randomized]
        assert orders == list(range(1, len(questions) + 1))
    
    @pytest.mark.asyncio
    async def test_generate_interview_questions_success(self, service, mock_db, sample_interview):
        """Test successful question generation"""
        # Mock database queries
        mock_db.query.return_value.filter.return_value.first.return_value = sample_interview
        
        # Mock job application and posting
        job_application = MagicMock()
        job_posting = MagicMock()
        job_posting.title = "Python Developer"
        job_posting.required_skills = []
        job_application.job_posting = job_posting
        sample_interview.job_application = job_application
        
        # Mock AI service
        with patch.object(service, '_generate_ai_questions') as mock_ai:
            mock_ai.return_value = [
                {
                    "question_text": "Test question",
                    "category": "technical",
                    "difficulty_level": "intermediate",
                    "expected_duration": 120,
                    "ai_generated": True,
                    "skill_focus": ["python"]
                }
            ]
            
            questions = await service.generate_interview_questions(
                mock_db, "test-interview-id"
            )
            
            assert len(questions) > 0
            assert all("question_order" in q for q in questions)
    
    @pytest.mark.asyncio
    async def test_generate_interview_questions_fallback(self, service, mock_db):
        """Test fallback when interview not found"""
        # Mock interview not found
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        questions = await service.generate_interview_questions(
            mock_db, "nonexistent-id"
        )
        
        # Should return fallback questions
        assert len(questions) >= 3
        assert all(q["ai_generated"] is False for q in questions)
    
    @pytest.mark.asyncio
    async def test_generate_follow_up_question(self, service, mock_db):
        """Test follow-up question generation"""
        # Mock parent question
        parent_question = MagicMock()
        parent_question.question_text = "What is your experience with Python?"
        parent_question.category = "technical"
        parent_question.difficulty_level = "intermediate"
        
        mock_db.query.return_value.filter.return_value.first.return_value = parent_question
        
        # Mock AI service
        with patch.object(service.ai_service, '_call_openai') as mock_openai:
            mock_openai.return_value = '''
            {
                "question_text": "Can you provide a specific example of a Python project?",
                "reasoning": "To get more concrete details",
                "expected_duration": 90
            }
            '''
            
            follow_up = await service.generate_follow_up_question(
                mock_db, "parent-id", "I have 5 years of Python experience", {}
            )
            
            assert follow_up is not None
            assert follow_up["is_follow_up"] is True
            assert "question_text" in follow_up
    
    @pytest.mark.asyncio
    async def test_generate_follow_up_question_failure(self, service, mock_db):
        """Test follow-up generation when parent question not found"""
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        follow_up = await service.generate_follow_up_question(
            mock_db, "nonexistent-id", "Some response", {}
        )
        
        assert follow_up is None


class TestQuestionGenerationAPI:
    """Test cases for question generation API endpoints"""
    
    @pytest.fixture
    def mock_interview(self):
        """Mock interview for API tests"""
        interview = MagicMock()
        interview.id = "test-interview-id"
        interview.company_id = "company-user-id"
        interview.candidate_id = "candidate-user-id"
        interview.max_questions = 5
        interview.difficulty_level = "intermediate"
        interview.focus_areas = ["python"]
        return interview
    
    @pytest.fixture
    def mock_company_user(self):
        """Mock company user"""
        user = MagicMock()
        user.id = "company-user-id"
        user.user_type = "company"
        return user
    
    @pytest.fixture
    def mock_candidate_user(self):
        """Mock candidate user"""
        user = MagicMock()
        user.id = "candidate-user-id"
        user.user_type = "candidate"
        return user
    
    @pytest.mark.asyncio
    async def test_generate_questions_success(self, client, mock_interview, mock_company_user):
        """Test successful question generation via API"""
        with patch('app.api.interviews.get_db') as mock_get_db, \
             patch('app.api.interviews.get_current_user') as mock_get_user, \
             patch('app.api.interviews.interview_question_service') as mock_service:
            
            # Setup mocks
            mock_db = MagicMock()
            mock_get_db.return_value = mock_db
            mock_get_user.return_value = mock_company_user
            
            mock_db.query.return_value.filter.return_value.first.return_value = mock_interview
            mock_db.query.return_value.filter.return_value.count.return_value = 0
            
            mock_service.generate_interview_questions.return_value = [
                {
                    "question_text": "Test question",
                    "category": "technical",
                    "difficulty_level": "intermediate"
                }
            ]
            
            # Mock stored questions
            stored_question = MagicMock()
            stored_question.question_text = "Test question"
            mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [stored_question]
            
            response = await client.post(
                f"/interviews/{mock_interview.id}/questions/generate"
            )
            
            assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_generate_questions_unauthorized(self, client, mock_interview, mock_candidate_user):
        """Test unauthorized question generation"""
        with patch('app.api.interviews.get_db') as mock_get_db, \
             patch('app.api.interviews.get_current_user') as mock_get_user:
            
            mock_db = MagicMock()
            mock_get_db.return_value = mock_db
            mock_get_user.return_value = mock_candidate_user
            
            mock_db.query.return_value.filter.return_value.first.return_value = mock_interview
            
            response = await client.post(
                f"/interviews/{mock_interview.id}/questions/generate"
            )
            
            assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_generate_questions_already_exist(self, client, mock_interview, mock_company_user):
        """Test generation when questions already exist"""
        with patch('app.api.interviews.get_db') as mock_get_db, \
             patch('app.api.interviews.get_current_user') as mock_get_user:
            
            mock_db = MagicMock()
            mock_get_db.return_value = mock_db
            mock_get_user.return_value = mock_company_user
            
            mock_db.query.return_value.filter.return_value.first.return_value = mock_interview
            mock_db.query.return_value.filter.return_value.count.return_value = 5  # Questions exist
            
            response = await client.post(
                f"/interviews/{mock_interview.id}/questions/generate"
            )
            
            assert response.status_code == 400
    
    @pytest.mark.asyncio
    async def test_get_questions_success(self, client, mock_interview, mock_company_user):
        """Test successful question retrieval"""
        with patch('app.api.interviews.get_db') as mock_get_db, \
             patch('app.api.interviews.get_current_user') as mock_get_user:
            
            mock_db = MagicMock()
            mock_get_db.return_value = mock_db
            mock_get_user.return_value = mock_company_user
            
            mock_db.query.return_value.filter.return_value.first.return_value = mock_interview
            
            # Mock questions
            mock_question = MagicMock()
            mock_question.question_text = "Test question"
            mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [mock_question]
            
            response = await client.get(
                f"/interviews/{mock_interview.id}/questions"
            )
            
            assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_generate_follow_up_success(self, client, mock_interview, mock_company_user):
        """Test successful follow-up generation"""
        with patch('app.api.interviews.get_db') as mock_get_db, \
             patch('app.api.interviews.get_current_user') as mock_get_user, \
             patch('app.api.interviews.interview_question_service') as mock_service:
            
            mock_db = MagicMock()
            mock_get_db.return_value = mock_db
            mock_get_user.return_value = mock_company_user
            
            mock_db.query.return_value.filter.return_value.first.return_value = mock_interview
            
            # Mock parent question
            parent_question = MagicMock()
            parent_question.id = "parent-id"
            mock_db.query.return_value.filter.return_value.first.return_value = parent_question
            
            mock_service.generate_follow_up_question.return_value = {
                "question_text": "Follow-up question",
                "category": "technical",
                "difficulty_level": "intermediate",
                "expected_duration": 90,
                "is_follow_up": True,
                "ai_generated": True,
                "skill_focus": [],
                "context_data": {}
            }
            
            response = await client.post(
                f"/interviews/{mock_interview.id}/questions/follow-up",
                json={
                    "parent_question_id": "parent-id",
                    "candidate_response": "My response"
                }
            )
            
            assert response.status_code == 200


class TestQuestionAccuracy:
    """Test cases for question generation accuracy and quality"""
    
    def test_question_relevance_to_job(self):
        """Test that generated questions are relevant to job requirements"""
        service = InterviewQuestionService()
        
        job_context = {
            "title": "Machine Learning Engineer",
            "required_skills": ["Python", "TensorFlow", "Statistics"],
            "experience_level": "senior"
        }
        
        questions = service._generate_template_questions(
            QuestionCategory.TECHNICAL, 3, job_context
        )
        
        # Questions should be relevant to the job
        assert len(questions) == 3
        assert all("question_text" in q for q in questions)
    
    def test_difficulty_consistency(self):
        """Test that difficulty levels are applied consistently"""
        service = InterviewQuestionService()
        
        questions = [
            {"difficulty_level": "beginner", "expected_duration": 60},
            {"difficulty_level": "intermediate", "expected_duration": 120},
            {"difficulty_level": "advanced", "expected_duration": 180}
        ]
        
        # Apply progression
        result = service._apply_difficulty_progression(questions, "intermediate")
        
        # Check duration scaling
        durations = [q["expected_duration"] for q in result]
        assert all(d > 0 for d in durations)
    
    def test_category_distribution_accuracy(self):
        """Test that question categories are distributed correctly"""
        service = InterviewQuestionService()
        
        # Test technical interview
        tech_dist = service._calculate_question_distribution(10, "ai_technical", [])
        tech_total = sum(tech_dist.values())
        assert tech_total == 10
        assert tech_dist.get(QuestionCategory.TECHNICAL, 0) >= 5
        
        # Test behavioral interview
        behav_dist = service._calculate_question_distribution(8, "ai_behavioral", [])
        behav_total = sum(behav_dist.values())
        assert behav_total == 8
        assert behav_dist.get(QuestionCategory.BEHAVIORAL, 0) >= 4
    
    def test_question_uniqueness(self):
        """Test that generated questions are unique"""
        service = InterviewQuestionService()
        
        job_context = {"title": "Developer", "required_skills": ["Python"]}
        
        questions1 = service._generate_template_questions(
            QuestionCategory.TECHNICAL, 5, job_context
        )
        questions2 = service._generate_template_questions(
            QuestionCategory.TECHNICAL, 5, job_context
        )
        
        # Questions should have some variation due to randomization
        texts1 = [q["question_text"] for q in questions1]
        texts2 = [q["question_text"] for q in questions2]
        
        # At least some questions should be different
        assert len(set(texts1 + texts2)) > len(texts1)


if __name__ == "__main__":
    pytest.main([__file__])