from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from uuid import UUID
import uuid
import secrets

from ..models.assessment import (
    Assessment, Question, AssessmentQuestion, AssessmentResponse,
    AssessmentType, QuestionType, DifficultyLevel, AssessmentStatus
)
from ..schemas.assessment import (
    AssessmentCreate, AssessmentUpdate, QuestionCreate, QuestionUpdate,
    AssessmentResponseCreate, GenerateQuestionsRequest, AIAnalysisResult
)
from .ai_service import AIService


class AssessmentService:
    def __init__(self, db: Session):
        self.db = db
        self.ai_service = AIService()
    
    # Question management
    async def create_question(self, question_data: QuestionCreate) -> Question:
        """Create a new question"""
        
        question = Question(
            **question_data.dict(),
            id=uuid.uuid4()
        )
        
        self.db.add(question)
        self.db.commit()
        self.db.refresh(question)
        
        return question
    
    async def generate_questions_with_ai(self, request: GenerateQuestionsRequest) -> List[Question]:
        """Generate questions using AI and save them to database"""
        
        # Generate questions using AI
        generated_questions = await self.ai_service.generate_questions(request)
        
        # Save to database
        questions = []
        for q_data in generated_questions:
            question = Question(
                id=uuid.uuid4(),
                title=q_data["title"],
                content=q_data["content"],
                question_type=QuestionType(q_data["question_type"]),
                difficulty_level=DifficultyLevel(q_data["difficulty_level"]),
                category=q_data["category"],
                tags=q_data.get("tags", []),
                options=q_data.get("options"),
                correct_answer=q_data.get("correct_answer"),
                explanation=q_data.get("explanation"),
                code_template=q_data.get("code_template"),
                test_cases=q_data.get("test_cases"),
                max_points=q_data.get("max_points", 10),
                ai_generated=q_data.get("ai_generated", True),
                generation_prompt=q_data.get("generation_prompt")
            )
            
            self.db.add(question)
            questions.append(question)
        
        self.db.commit()
        
        for question in questions:
            self.db.refresh(question)
        
        return questions
    
    def get_questions(self, 
                     category: Optional[str] = None,
                     difficulty: Optional[DifficultyLevel] = None,
                     question_type: Optional[QuestionType] = None,
                     limit: int = 50) -> List[Question]:
        """Get questions with optional filtering"""
        
        query = self.db.query(Question).filter(Question.is_active == True)
        
        if category:
            query = query.filter(Question.category == category)
        if difficulty:
            query = query.filter(Question.difficulty_level == difficulty)
        if question_type:
            query = query.filter(Question.question_type == question_type)
        
        return query.limit(limit).all()
    
    def get_question_by_id(self, question_id: UUID) -> Optional[Question]:
        """Get question by ID"""
        return self.db.query(Question).filter(Question.id == question_id).first()
    
    def update_question(self, question_id: UUID, question_data: QuestionUpdate) -> Optional[Question]:
        """Update question"""
        
        question = self.get_question_by_id(question_id)
        if not question:
            return None
        
        update_data = question_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(question, field, value)
        
        self.db.commit()
        self.db.refresh(question)
        
        return question
    
    # Assessment management
    async def create_assessment(self, assessment_data: AssessmentCreate) -> Assessment:
        """Create a new assessment"""
        
        # Create assessment
        assessment = Assessment(
            id=uuid.uuid4(),
            candidate_id=assessment_data.candidate_id,
            job_posting_id=assessment_data.job_posting_id,
            title=assessment_data.title,
            description=assessment_data.description,
            assessment_type=assessment_data.assessment_type,
            duration_minutes=assessment_data.duration_minutes,
            passing_score=assessment_data.passing_score,
            total_questions=len(assessment_data.question_ids),
            expires_at=datetime.utcnow() + timedelta(days=7)  # Default 7 days to complete
        )
        
        self.db.add(assessment)
        self.db.flush()  # Get the ID
        
        # Add questions to assessment
        for i, question_id in enumerate(assessment_data.question_ids):
            question = self.get_question_by_id(question_id)
            if question:
                assessment_question = AssessmentQuestion(
                    id=uuid.uuid4(),
                    assessment_id=assessment.id,
                    question_id=question_id,
                    order_index=i,
                    points=question.max_points,
                    time_limit_seconds=question.time_limit_seconds
                )
                self.db.add(assessment_question)
        
        self.db.commit()
        self.db.refresh(assessment)
        
        return assessment
    
    def get_assessment_by_id(self, assessment_id: UUID) -> Optional[Assessment]:
        """Get assessment by ID with questions"""
        return self.db.query(Assessment).filter(Assessment.id == assessment_id).first()
    
    def get_candidate_assessments(self, candidate_id: UUID) -> List[Assessment]:
        """Get all assessments for a candidate"""
        return self.db.query(Assessment).filter(Assessment.candidate_id == candidate_id).all()
    
    async def start_assessment(self, assessment_id: UUID) -> Dict[str, Any]:
        """Start an assessment session"""
        
        assessment = self.get_assessment_by_id(assessment_id)
        if not assessment:
            raise ValueError("Assessment not found")
        
        if assessment.status != AssessmentStatus.NOT_STARTED:
            raise ValueError("Assessment already started or completed")
        
        if assessment.expires_at and assessment.expires_at < datetime.utcnow():
            assessment.status = AssessmentStatus.EXPIRED
            self.db.commit()
            raise ValueError("Assessment has expired")
        
        # Update assessment status
        assessment.status = AssessmentStatus.IN_PROGRESS
        assessment.started_at = datetime.utcnow()
        
        self.db.commit()
        
        # Generate session token
        session_token = secrets.token_urlsafe(32)
        
        # Get first question
        first_question_rel = self.db.query(AssessmentQuestion).filter(
            AssessmentQuestion.assessment_id == assessment_id,
            AssessmentQuestion.order_index == 0
        ).first()
        
        first_question = None
        if first_question_rel:
            first_question = self.get_question_by_id(first_question_rel.question_id)
        
        return {
            "assessment_id": assessment_id,
            "session_token": session_token,
            "expires_at": datetime.utcnow() + timedelta(minutes=assessment.duration_minutes),
            "first_question": first_question
        }
    
    async def submit_response(self, 
                            assessment_id: UUID, 
                            response_data: AssessmentResponseCreate) -> AssessmentResponse:
        """Submit a response to a question"""
        
        assessment = self.get_assessment_by_id(assessment_id)
        if not assessment or assessment.status != AssessmentStatus.IN_PROGRESS:
            raise ValueError("Invalid assessment or not in progress")
        
        question = self.get_question_by_id(response_data.question_id)
        if not question:
            raise ValueError("Question not found")
        
        # Check if response already exists
        existing_response = self.db.query(AssessmentResponse).filter(
            and_(
                AssessmentResponse.assessment_id == assessment_id,
                AssessmentResponse.question_id == response_data.question_id
            )
        ).first()
        
        if existing_response:
            # Update existing response
            existing_response.response_text = response_data.response_text
            existing_response.selected_options = response_data.selected_options
            existing_response.code_solution = response_data.code_solution
            existing_response.submitted_at = datetime.utcnow()
            
            response = existing_response
        else:
            # Create new response
            response = AssessmentResponse(
                id=uuid.uuid4(),
                assessment_id=assessment_id,
                question_id=response_data.question_id,
                response_text=response_data.response_text,
                selected_options=response_data.selected_options,
                code_solution=response_data.code_solution,
                started_at=datetime.utcnow(),
                submitted_at=datetime.utcnow()
            )
            self.db.add(response)
        
        # Evaluate response using AI
        question_dict = {
            "content": question.content,
            "correct_answer": question.correct_answer,
            "explanation": question.explanation,
            "max_points": question.max_points,
            "test_cases": question.test_cases,
            "category": question.category
        }
        
        response_text = (response_data.response_text or 
                        str(response_data.selected_options) or 
                        response_data.code_solution or "")
        
        evaluation = await self.ai_service.evaluate_response(
            question_dict, response_text, question.question_type
        )
        
        # Update response with evaluation
        response.points_earned = evaluation["points_earned"]
        response.is_correct = evaluation["is_correct"]
        response.ai_feedback = evaluation["ai_feedback"]
        response.ai_score_breakdown = evaluation["ai_score_breakdown"]
        
        self.db.commit()
        self.db.refresh(response)
        
        return response
    
    def get_next_question(self, assessment_id: UUID, current_question_index: int) -> Dict[str, Any]:
        """Get the next question in the assessment"""
        
        assessment = self.get_assessment_by_id(assessment_id)
        if not assessment:
            raise ValueError("Assessment not found")
        
        next_index = current_question_index + 1
        
        next_question_rel = self.db.query(AssessmentQuestion).filter(
            AssessmentQuestion.assessment_id == assessment_id,
            AssessmentQuestion.order_index == next_index
        ).first()
        
        if next_question_rel:
            next_question = self.get_question_by_id(next_question_rel.question_id)
            
            # Calculate time remaining
            if assessment.started_at:
                elapsed_minutes = (datetime.utcnow() - assessment.started_at).total_seconds() / 60
                time_remaining_seconds = max(0, (assessment.duration_minutes - elapsed_minutes) * 60)
            else:
                time_remaining_seconds = assessment.duration_minutes * 60
            
            return {
                "question": next_question,
                "question_index": next_index,
                "total_questions": assessment.total_questions,
                "time_remaining_seconds": int(time_remaining_seconds),
                "is_last_question": next_index >= assessment.total_questions - 1
            }
        else:
            return {
                "question": None,
                "question_index": next_index,
                "total_questions": assessment.total_questions,
                "time_remaining_seconds": 0,
                "is_last_question": True
            }
    
    async def complete_assessment(self, assessment_id: UUID) -> Dict[str, Any]:
        """Complete an assessment and calculate final scores"""
        
        assessment = self.get_assessment_by_id(assessment_id)
        if not assessment:
            raise ValueError("Assessment not found")
        
        if assessment.status != AssessmentStatus.IN_PROGRESS:
            raise ValueError("Assessment not in progress")
        
        # Get all responses
        responses = self.db.query(AssessmentResponse).filter(
            AssessmentResponse.assessment_id == assessment_id
        ).all()
        
        # Get all questions
        assessment_questions = self.db.query(AssessmentQuestion).filter(
            AssessmentQuestion.assessment_id == assessment_id
        ).all()
        
        questions = []
        for aq in assessment_questions:
            question = self.get_question_by_id(aq.question_id)
            if question:
                questions.append(question)
        
        # Calculate scores
        total_points_earned = sum(r.points_earned or 0 for r in responses)
        total_possible_points = sum(q.max_points for q in questions)
        
        percentage_score = (total_points_earned / total_possible_points * 100) if total_possible_points > 0 else 0
        passed = percentage_score >= assessment.passing_score
        
        # Perform AI analysis
        response_data = []
        for response in responses:
            response_data.append({
                "points_earned": response.points_earned,
                "is_correct": response.is_correct,
                "ai_score_breakdown": response.ai_score_breakdown
            })
        
        question_data = []
        for question in questions:
            question_data.append({
                "category": question.category,
                "max_points": question.max_points,
                "difficulty_level": question.difficulty_level.value
            })
        
        ai_analysis = await self.ai_service.analyze_assessment_results(response_data, question_data)
        
        # Update assessment
        assessment.status = AssessmentStatus.COMPLETED
        assessment.completed_at = datetime.utcnow()
        assessment.total_score = total_points_earned
        assessment.percentage_score = percentage_score
        assessment.passed = passed
        assessment.skill_scores = ai_analysis.skill_breakdown
        assessment.ai_analysis = {
            "overall_score": ai_analysis.overall_score,
            "strengths": ai_analysis.strengths,
            "weaknesses": ai_analysis.weaknesses,
            "recommendations": ai_analysis.recommendations,
            "confidence_level": ai_analysis.confidence_level
        }
        
        self.db.commit()
        
        return {
            "assessment_id": assessment_id,
            "total_score": total_points_earned,
            "percentage_score": percentage_score,
            "passed": passed,
            "skill_scores": ai_analysis.skill_breakdown,
            "ai_analysis": assessment.ai_analysis
        }
    
    def get_assessment_results(self, assessment_id: UUID) -> Optional[Dict[str, Any]]:
        """Get detailed assessment results"""
        
        assessment = self.get_assessment_by_id(assessment_id)
        if not assessment or assessment.status != AssessmentStatus.COMPLETED:
            return None
        
        # Get responses with questions
        responses = self.db.query(AssessmentResponse).filter(
            AssessmentResponse.assessment_id == assessment_id
        ).all()
        
        response_details = []
        for response in responses:
            question = self.get_question_by_id(response.question_id)
            if question:
                response_details.append({
                    "question": {
                        "id": question.id,
                        "title": question.title,
                        "content": question.content,
                        "category": question.category,
                        "max_points": question.max_points
                    },
                    "response": {
                        "response_text": response.response_text,
                        "selected_options": response.selected_options,
                        "code_solution": response.code_solution,
                        "points_earned": response.points_earned,
                        "is_correct": response.is_correct,
                        "ai_feedback": response.ai_feedback
                    }
                })
        
        return {
            "assessment": {
                "id": assessment.id,
                "title": assessment.title,
                "assessment_type": assessment.assessment_type.value,
                "total_score": assessment.total_score,
                "percentage_score": assessment.percentage_score,
                "passed": assessment.passed,
                "completed_at": assessment.completed_at
            },
            "skill_scores": assessment.skill_scores,
            "ai_analysis": assessment.ai_analysis,
            "responses": response_details
        }