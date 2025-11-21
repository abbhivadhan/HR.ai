import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from uuid import uuid4
import json

from app.main import app
from app.database import Base, get_db
from app.models.user import User, UserType
from app.models.assessment import (
    Assessment, Question, AssessmentQuestion, AssessmentResponse,
    AssessmentType, QuestionType, DifficultyLevel, AssessmentStatus
)
from app.auth.utils import create_access_token

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_assessments.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture
def db_session():
    """Create a fresh database session for each test"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def test_user(db_session):
    """Create a test candidate user"""
    user = User(
        id=uuid4(),
        email="candidate@test.com",
        password_hash="hashed_password",
        first_name="Test",
        last_name="Candidate",
        user_type=UserType.CANDIDATE,
        is_active=True,
        is_verified=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_company_user(db_session):
    """Create a test company user"""
    user = User(
        id=uuid4(),
        email="company@test.com",
        password_hash="hashed_password",
        first_name="Test",
        last_name="Company",
        user_type=UserType.COMPANY,
        is_active=True,
        is_verified=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_admin_user(db_session):
    """Create a test admin user"""
    user = User(
        id=uuid4(),
        email="admin@test.com",
        password_hash="hashed_password",
        first_name="Test",
        last_name="Admin",
        user_type=UserType.ADMIN,
        is_active=True,
        is_verified=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_questions(db_session):
    """Create test questions"""
    questions = []
    
    # Multiple choice question
    q1 = Question(
        id=uuid4(),
        title="Python Basics",
        content="What is the output of print(2 + 2)?",
        question_type=QuestionType.MULTIPLE_CHOICE,
        difficulty_level=DifficultyLevel.BEGINNER,
        category="python",
        options={"A": "3", "B": "4", "C": "5", "D": "Error"},
        correct_answer="B",
        explanation="2 + 2 equals 4",
        max_points=10
    )
    
    # Coding question
    q2 = Question(
        id=uuid4(),
        title="FizzBuzz Implementation",
        content="Write a function that prints numbers 1-100, but prints 'Fizz' for multiples of 3 and 'Buzz' for multiples of 5",
        question_type=QuestionType.CODING,
        difficulty_level=DifficultyLevel.INTERMEDIATE,
        category="algorithms",
        code_template="def fizzbuzz():\n    # Your code here\n    pass",
        test_cases=[
            {"input": "15", "expected": "FizzBuzz"},
            {"input": "9", "expected": "Fizz"},
            {"input": "10", "expected": "Buzz"}
        ],
        max_points=20
    )
    
    # Text response question
    q3 = Question(
        id=uuid4(),
        title="System Design",
        content="Explain how you would design a scalable web application",
        question_type=QuestionType.TEXT_RESPONSE,
        difficulty_level=DifficultyLevel.ADVANCED,
        category="system_design",
        max_points=15
    )
    
    questions = [q1, q2, q3]
    
    for question in questions:
        db_session.add(question)
    
    db_session.commit()
    
    for question in questions:
        db_session.refresh(question)
    
    return questions


@pytest.fixture
def auth_headers(test_user):
    """Create authentication headers for test user"""
    token = create_access_token(data={"sub": test_user.email})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_auth_headers(test_admin_user):
    """Create authentication headers for admin user"""
    token = create_access_token(data={"sub": test_admin_user.email})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def company_auth_headers(test_company_user):
    """Create authentication headers for company user"""
    token = create_access_token(data={"sub": test_company_user.email})
    return {"Authorization": f"Bearer {token}"}


class TestQuestionManagement:
    """Test question CRUD operations"""
    
    def test_create_question_as_admin(self, admin_auth_headers):
        """Test creating a question as admin"""
        question_data = {
            "title": "Test Question",
            "content": "What is 2 + 2?",
            "question_type": "multiple_choice",
            "difficulty_level": "beginner",
            "category": "math",
            "options": {"A": "3", "B": "4", "C": "5"},
            "correct_answer": "B",
            "max_points": 10
        }
        
        response = client.post(
            "/api/assessments/questions",
            json=question_data,
            headers=admin_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == question_data["title"]
        assert data["question_type"] == question_data["question_type"]
    
    def test_create_question_as_candidate_forbidden(self, auth_headers):
        """Test that candidates cannot create questions"""
        question_data = {
            "title": "Test Question",
            "content": "What is 2 + 2?",
            "question_type": "multiple_choice",
            "difficulty_level": "beginner",
            "category": "math",
            "max_points": 10
        }
        
        response = client.post(
            "/api/assessments/questions",
            json=question_data,
            headers=auth_headers
        )
        
        assert response.status_code == 403
    
    def test_get_questions(self, test_questions, auth_headers):
        """Test getting questions list"""
        response = client.get(
            "/api/assessments/questions",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert any(q["category"] == "python" for q in data)
    
    def test_get_questions_with_filters(self, test_questions, auth_headers):
        """Test getting questions with filters"""
        response = client.get(
            "/api/assessments/questions?category=python&difficulty=beginner",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["category"] == "python"
        assert data[0]["difficulty_level"] == "beginner"
    
    def test_get_question_by_id(self, test_questions, auth_headers):
        """Test getting a specific question"""
        question_id = test_questions[0].id
        
        response = client.get(
            f"/api/assessments/questions/{question_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(question_id)
        assert data["title"] == test_questions[0].title


class TestAssessmentManagement:
    """Test assessment CRUD operations"""
    
    def test_create_assessment(self, test_user, test_questions, company_auth_headers):
        """Test creating an assessment"""
        assessment_data = {
            "candidate_id": str(test_user.id),
            "title": "Python Developer Assessment",
            "description": "Technical assessment for Python developer position",
            "assessment_type": "technical",
            "duration_minutes": 60,
            "passing_score": 70.0,
            "question_ids": [str(q.id) for q in test_questions]
        }
        
        response = client.post(
            "/api/assessments/",
            json=assessment_data,
            headers=company_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == assessment_data["title"]
        assert data["candidate_id"] == assessment_data["candidate_id"]
        assert data["total_questions"] == len(test_questions)
    
    def test_get_candidate_assessments(self, test_user, test_questions, company_auth_headers, auth_headers, db_session):
        """Test getting assessments for a candidate"""
        # First create an assessment
        assessment = Assessment(
            id=uuid4(),
            candidate_id=test_user.id,
            title="Test Assessment",
            assessment_type=AssessmentType.TECHNICAL,
            duration_minutes=60,
            total_questions=1,
            passing_score=70.0
        )
        db_session.add(assessment)
        db_session.commit()
        
        # Get assessments as candidate
        response = client.get(
            "/api/assessments/",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any(a["id"] == str(assessment.id) for a in data)


class TestAssessmentSession:
    """Test assessment taking workflow"""
    
    @pytest.fixture
    def test_assessment(self, test_user, test_questions, db_session):
        """Create a test assessment with questions"""
        assessment = Assessment(
            id=uuid4(),
            candidate_id=test_user.id,
            title="Test Assessment",
            assessment_type=AssessmentType.TECHNICAL,
            duration_minutes=60,
            total_questions=len(test_questions),
            passing_score=70.0,
            status=AssessmentStatus.NOT_STARTED
        )
        db_session.add(assessment)
        db_session.flush()
        
        # Add questions to assessment
        for i, question in enumerate(test_questions):
            assessment_question = AssessmentQuestion(
                id=uuid4(),
                assessment_id=assessment.id,
                question_id=question.id,
                order_index=i,
                points=question.max_points
            )
            db_session.add(assessment_question)
        
        db_session.commit()
        db_session.refresh(assessment)
        return assessment
    
    def test_start_assessment(self, test_assessment, auth_headers):
        """Test starting an assessment"""
        response = client.post(
            f"/api/assessments/{test_assessment.id}/start",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["assessment_id"] == str(test_assessment.id)
        assert "session_token" in data
        assert "first_question" in data
    
    def test_submit_response(self, test_assessment, test_questions, auth_headers, db_session):
        """Test submitting a response"""
        # Start assessment first
        test_assessment.status = AssessmentStatus.IN_PROGRESS
        db_session.commit()
        
        response_data = {
            "question_id": str(test_questions[0].id),
            "response": {
                "selected_options": ["B"]
            }
        }
        
        response = client.post(
            f"/api/assessments/{test_assessment.id}/responses",
            json=response_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["question_id"] == response_data["question_id"]
        assert data["selected_options"] == response_data["response"]["selected_options"]
    
    def test_get_next_question(self, test_assessment, auth_headers, db_session):
        """Test getting next question"""
        # Start assessment first
        test_assessment.status = AssessmentStatus.IN_PROGRESS
        db_session.commit()
        
        response = client.get(
            f"/api/assessments/{test_assessment.id}/next-question?current_index=0",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "question" in data
        assert data["question_index"] == 1
        assert data["total_questions"] == test_assessment.total_questions
    
    def test_complete_assessment(self, test_assessment, auth_headers, db_session):
        """Test completing an assessment"""
        # Start assessment first
        test_assessment.status = AssessmentStatus.IN_PROGRESS
        db_session.commit()
        
        response = client.post(
            f"/api/assessments/{test_assessment.id}/complete",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["assessment_id"] == str(test_assessment.id)
        assert "total_score" in data
        assert "percentage_score" in data
        assert "passed" in data


class TestAIIntegration:
    """Test AI-powered features"""
    
    def test_generate_questions_request(self, company_auth_headers):
        """Test AI question generation request format"""
        request_data = {
            "job_title": "Python Developer",
            "required_skills": ["python", "django", "postgresql"],
            "difficulty_level": "intermediate",
            "question_count": 5,
            "question_types": ["multiple_choice", "coding"]
        }
        
        # Note: This will use fallback questions since OpenAI key might not be configured
        response = client.post(
            "/api/assessments/questions/generate",
            json=request_data,
            headers=company_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= request_data["question_count"]
        assert all("title" in q for q in data)
        assert all("content" in q for q in data)


class TestPermissions:
    """Test access control and permissions"""
    
    def test_candidate_cannot_access_other_assessment(self, test_user, test_company_user, test_questions, auth_headers, db_session):
        """Test that candidates can only access their own assessments"""
        # Create assessment for different user
        other_user = User(
            id=uuid4(),
            email="other@test.com",
            password_hash="hashed",
            first_name="Other",
            last_name="User",
            user_type=UserType.CANDIDATE
        )
        db_session.add(other_user)
        db_session.commit()
        
        assessment = Assessment(
            id=uuid4(),
            candidate_id=other_user.id,
            title="Other's Assessment",
            assessment_type=AssessmentType.TECHNICAL,
            duration_minutes=60,
            total_questions=1,
            passing_score=70.0
        )
        db_session.add(assessment)
        db_session.commit()
        
        # Try to access other user's assessment
        response = client.get(
            f"/api/assessments/{assessment.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 403
    
    def test_unauthenticated_access_denied(self):
        """Test that unauthenticated requests are denied"""
        response = client.get("/api/assessments/questions")
        assert response.status_code == 401


if __name__ == "__main__":
    pytest.main([__file__])