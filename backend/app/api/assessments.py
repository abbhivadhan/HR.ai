from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from ..database import get_db
from ..auth.dependencies import get_current_user
from ..models.user import User
from ..models.assessment import AssessmentType, QuestionType, DifficultyLevel
from ..schemas.assessment import (
    Assessment, AssessmentCreate, AssessmentUpdate,
    Question, QuestionCreate, QuestionUpdate,
    AssessmentResponse, AssessmentResponseCreate,
    StartAssessmentResponse, SubmitResponseRequest,
    NextQuestionResponse, CompleteAssessmentResponse,
    GenerateQuestionsRequest
)
from ..services.assessment_service import AssessmentService

router = APIRouter(prefix="/assessments", tags=["assessments"])


# Question endpoints
@router.post("/questions", response_model=Question)
async def create_question(
    question_data: QuestionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new question (admin only)"""
    
    if current_user.user_type.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can create questions"
        )
    
    service = AssessmentService(db)
    return await service.create_question(question_data)


@router.post("/questions/generate", response_model=List[Question])
async def generate_questions(
    request: GenerateQuestionsRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate questions using AI"""
    
    if current_user.user_type.value not in ["admin", "company"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators and companies can generate questions"
        )
    
    service = AssessmentService(db)
    return await service.generate_questions_with_ai(request)


@router.get("/questions", response_model=List[Question])
async def get_questions(
    category: Optional[str] = None,
    difficulty: Optional[DifficultyLevel] = None,
    question_type: Optional[QuestionType] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get questions with optional filtering"""
    
    service = AssessmentService(db)
    return service.get_questions(category, difficulty, question_type, limit)


@router.get("/questions/{question_id}", response_model=Question)
async def get_question(
    question_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get question by ID"""
    
    service = AssessmentService(db)
    question = service.get_question_by_id(question_id)
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    return question


@router.put("/questions/{question_id}", response_model=Question)
async def update_question(
    question_id: UUID,
    question_data: QuestionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update question (admin only)"""
    
    if current_user.user_type.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can update questions"
        )
    
    service = AssessmentService(db)
    question = service.update_question(question_id, question_data)
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    return question


# Assessment endpoints
@router.post("/", response_model=Assessment)
async def create_assessment(
    assessment_data: AssessmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new assessment"""
    
    # Only companies can create assessments for candidates
    if current_user.user_type.value not in ["admin", "company"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only companies and administrators can create assessments"
        )
    
    service = AssessmentService(db)
    return await service.create_assessment(assessment_data)


@router.get("/", response_model=List[Assessment])
async def get_assessments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get assessments for current user"""
    
    service = AssessmentService(db)
    
    if current_user.user_type.value == "candidate":
        return service.get_candidate_assessments(current_user.id)
    else:
        # For companies/admins, implement company-specific logic
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Company assessment listing not implemented yet"
        )


@router.get("/{assessment_id}", response_model=Assessment)
async def get_assessment(
    assessment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get assessment by ID"""
    
    service = AssessmentService(db)
    assessment = service.get_assessment_by_id(assessment_id)
    
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )
    
    # Check permissions
    if (current_user.user_type.value == "candidate" and 
        assessment.candidate_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return assessment


@router.post("/{assessment_id}/start", response_model=StartAssessmentResponse)
async def start_assessment(
    assessment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Start an assessment session"""
    
    service = AssessmentService(db)
    assessment = service.get_assessment_by_id(assessment_id)
    
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )
    
    # Only the assigned candidate can start the assessment
    if assessment.candidate_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    try:
        result = service.start_assessment(assessment_id)
        return StartAssessmentResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{assessment_id}/responses", response_model=AssessmentResponse)
async def submit_response(
    assessment_id: UUID,
    request: SubmitResponseRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit a response to a question"""
    
    service = AssessmentService(db)
    assessment = service.get_assessment_by_id(assessment_id)
    
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )
    
    # Only the assigned candidate can submit responses
    if assessment.candidate_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    try:
        return await service.submit_response(assessment_id, request.response)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{assessment_id}/next-question", response_model=NextQuestionResponse)
async def get_next_question(
    assessment_id: UUID,
    current_index: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the next question in the assessment"""
    
    service = AssessmentService(db)
    assessment = service.get_assessment_by_id(assessment_id)
    
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )
    
    # Only the assigned candidate can get questions
    if assessment.candidate_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    try:
        result = service.get_next_question(assessment_id, current_index)
        return NextQuestionResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{assessment_id}/complete", response_model=CompleteAssessmentResponse)
async def complete_assessment(
    assessment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Complete an assessment and get final results"""
    
    service = AssessmentService(db)
    assessment = service.get_assessment_by_id(assessment_id)
    
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )
    
    # Only the assigned candidate can complete the assessment
    if assessment.candidate_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    try:
        result = await service.complete_assessment(assessment_id)
        return CompleteAssessmentResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{assessment_id}/results")
async def get_assessment_results(
    assessment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed assessment results"""
    
    service = AssessmentService(db)
    assessment = service.get_assessment_by_id(assessment_id)
    
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )
    
    # Check permissions - candidate or company that created the assessment
    if (current_user.user_type.value == "candidate" and 
        assessment.candidate_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    results = service.get_assessment_results(assessment_id)
    
    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment results not found or assessment not completed"
        )
    
    return results


# External Assessment Endpoints
@router.get("/external/tests")
async def get_external_tests(
    provider: Optional[str] = Query(None),
    skill: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get available external assessment tests"""
    try:
        if provider:
            tests = await external_assessment_service.get_tests_by_provider(provider)
        elif skill:
            tests = await external_assessment_service.get_tests_by_skill(skill)
        else:
            tests = await external_assessment_service.get_all_available_tests()
        
        return tests
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch external tests: {str(e)}"
        )


@router.post("/external/start")
async def start_external_test(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start an external assessment test"""
    try:
        provider = request.get("provider")
        test_id = request.get("test_id")
        
        if not provider or not test_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Provider and test_id are required"
            )
        
        # Create test session with external provider
        session = await external_assessment_service.create_test_session(
            provider_name=provider,
            test_id=test_id,
            candidate_email=current_user.email
        )
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create test session"
            )
        
        # TODO: Store session in database for tracking
        
        return {
            "session_id": session["session_id"],
            "test_url": session["test_url"],
            "expires_at": session["expires_at"],
            "status": session["status"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start external test: {str(e)}"
        )


@router.get("/external/results/{session_id}")
async def get_external_test_results(
    session_id: str,
    provider: str = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get results from external assessment"""
    try:
        results = await external_assessment_service.get_test_results(
            provider_name=provider,
            session_id=session_id
        )
        
        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test results not found"
            )
        
        return results
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch test results: {str(e)}"
        )


@router.get("/external/recommended")
async def get_recommended_tests(
    job_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get recommended external tests based on job requirements"""
    try:
        # TODO: Fetch job skills from database
        job_skills = ["Python", "JavaScript", "React", "SQL"]
        
        recommendations = external_assessment_service.get_recommended_tests(job_skills)
        return recommendations
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get recommendations: {str(e)}"
        )
