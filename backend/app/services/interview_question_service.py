"""
AI-powered interview question generation service
"""
import json
import logging
import random
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from enum import Enum

from ..models.interview import Interview, InterviewQuestion, QuestionCategory
from ..models.job import JobPosting
from ..models.profile import Skill
from ..services.ai_service import AIService
from ..config import settings

logger = logging.getLogger(__name__)


class QuestionDifficulty(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class InterviewQuestionService:
    """Service for generating and managing AI interview questions"""
    
    def __init__(self):
        self.ai_service = AIService()
        self.question_pools = self._initialize_question_pools()
        
    def _initialize_question_pools(self) -> Dict[str, List[Dict]]:
        """Initialize base question pools for different categories"""
        return {
            QuestionCategory.TECHNICAL: [
                {
                    "template": "Explain the concept of {concept} and provide a practical example.",
                    "concepts": ["object-oriented programming", "database normalization", "API design", "data structures"],
                    "difficulty": QuestionDifficulty.INTERMEDIATE,
                    "expected_duration": 180
                },
                {
                    "template": "How would you optimize {scenario} for better performance?",
                    "scenarios": ["a slow database query", "a web application", "memory usage", "network requests"],
                    "difficulty": QuestionDifficulty.ADVANCED,
                    "expected_duration": 240
                }
            ],
            QuestionCategory.BEHAVIORAL: [
                {
                    "template": "Tell me about a time when you {situation}. What was the outcome?",
                    "situations": ["faced a difficult technical challenge", "had to work with a difficult team member", 
                                 "missed a deadline", "had to learn a new technology quickly"],
                    "difficulty": QuestionDifficulty.INTERMEDIATE,
                    "expected_duration": 120
                },
                {
                    "template": "Describe a situation where you {action}. How did you handle it?",
                    "actions": ["disagreed with your manager", "had to give constructive feedback", 
                              "made a significant mistake", "led a team project"],
                    "difficulty": QuestionDifficulty.INTERMEDIATE,
                    "expected_duration": 150
                }
            ],
            QuestionCategory.SITUATIONAL: [
                {
                    "template": "If you were tasked with {task}, how would you approach it?",
                    "tasks": ["designing a new system from scratch", "debugging a production issue", 
                            "mentoring a junior developer", "implementing a new feature with tight deadlines"],
                    "difficulty": QuestionDifficulty.ADVANCED,
                    "expected_duration": 200
                }
            ]
        }

    async def generate_interview_questions(
        self, 
        db: Session, 
        interview_id: str, 
        job_requirements: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """Generate dynamic questions for an interview based on job requirements"""
        
        try:
            # Get interview details
            interview = db.query(Interview).filter(Interview.id == interview_id).first()
            if not interview:
                raise ValueError(f"Interview {interview_id} not found")
            
            # Get job posting details
            job_application = interview.job_application
            job_posting = job_application.job_posting if job_application else None
            
            # Determine question distribution
            question_distribution = self._calculate_question_distribution(
                interview.max_questions, 
                interview.interview_type,
                interview.focus_areas
            )
            
            # Generate questions for each category
            all_questions = []
            question_order = 1
            
            for category, count in question_distribution.items():
                if count > 0:
                    category_questions = await self._generate_category_questions(
                        db, interview, job_posting, category, count, question_order
                    )
                    all_questions.extend(category_questions)
                    question_order += len(category_questions)
            
            # Apply difficulty progression
            all_questions = self._apply_difficulty_progression(all_questions, interview.difficulty_level)
            
            # Store questions in database
            await self._store_questions(db, interview_id, all_questions)
            
            logger.info(f"Generated {len(all_questions)} questions for interview {interview_id}")
            return all_questions
            
        except Exception as e:
            logger.error(f"Error generating questions for interview {interview_id}: {e}")
            # Return fallback questions
            return await self._generate_fallback_questions(db, interview_id)

    def _calculate_question_distribution(
        self, 
        total_questions: int, 
        interview_type: str, 
        focus_areas: List[str]
    ) -> Dict[QuestionCategory, int]:
        """Calculate how many questions to generate for each category"""
        
        distribution = {}
        
        if interview_type == "ai_technical":
            # Technical interview focuses more on technical questions
            distribution[QuestionCategory.TECHNICAL] = max(1, int(total_questions * 0.7))
            distribution[QuestionCategory.PROBLEM_SOLVING] = max(1, int(total_questions * 0.2))
            distribution[QuestionCategory.BEHAVIORAL] = max(1, total_questions - 
                distribution[QuestionCategory.TECHNICAL] - distribution[QuestionCategory.PROBLEM_SOLVING])
            
        elif interview_type == "ai_behavioral":
            # Behavioral interview focuses on soft skills
            distribution[QuestionCategory.BEHAVIORAL] = max(1, int(total_questions * 0.6))
            distribution[QuestionCategory.SITUATIONAL] = max(1, int(total_questions * 0.3))
            distribution[QuestionCategory.COMPANY_CULTURE] = max(1, total_questions - 
                distribution[QuestionCategory.BEHAVIORAL] - distribution[QuestionCategory.SITUATIONAL])
            
        else:  # ai_screening or general
            # Balanced distribution for screening
            distribution[QuestionCategory.TECHNICAL] = max(1, int(total_questions * 0.4))
            distribution[QuestionCategory.BEHAVIORAL] = max(1, int(total_questions * 0.3))
            distribution[QuestionCategory.SITUATIONAL] = max(1, int(total_questions * 0.2))
            distribution[QuestionCategory.COMPANY_CULTURE] = max(1, total_questions - 
                sum(distribution.values()))
        
        # Adjust based on focus areas
        if focus_areas:
            for area in focus_areas:
                if "technical" in area.lower():
                    distribution[QuestionCategory.TECHNICAL] += 1
                elif "behavioral" in area.lower():
                    distribution[QuestionCategory.BEHAVIORAL] += 1
        
        return distribution

    async def _generate_category_questions(
        self,
        db: Session,
        interview: Interview,
        job_posting: Optional[JobPosting],
        category: QuestionCategory,
        count: int,
        start_order: int
    ) -> List[Dict[str, Any]]:
        """Generate questions for a specific category"""
        
        questions = []
        
        # Get job-specific context
        job_context = self._extract_job_context(job_posting) if job_posting else {}
        
        # Try AI generation first
        try:
            ai_questions = await self._generate_ai_questions(
                interview, job_context, category, count
            )
            questions.extend(ai_questions)
        except Exception as e:
            logger.warning(f"AI question generation failed for category {category}: {e}")
        
        # Fill remaining with template questions if needed
        if len(questions) < count:
            template_questions = self._generate_template_questions(
                category, count - len(questions), job_context
            )
            questions.extend(template_questions)
        
        # Add metadata to questions
        for i, question in enumerate(questions):
            question.update({
                "question_order": start_order + i,
                "category": category.value,
                "interview_id": str(interview.id),
                "generated_at": datetime.now().isoformat(),
                "is_follow_up": False,
                "parent_question_id": None
            })
        
        return questions[:count]

    async def _generate_ai_questions(
        self,
        interview: Interview,
        job_context: Dict,
        category: QuestionCategory,
        count: int
    ) -> List[Dict[str, Any]]:
        """Generate questions using AI based on job context"""
        
        prompt = self._build_question_prompt(interview, job_context, category, count)
        
        try:
            response = await self.ai_service._call_openai(prompt, max_tokens=2000)
            questions = self._parse_ai_questions(response, category)
            return questions[:count]
        except Exception as e:
            logger.error(f"AI question generation error: {e}")
            return []

    def _build_question_prompt(
        self,
        interview: Interview,
        job_context: Dict,
        category: QuestionCategory,
        count: int
    ) -> str:
        """Build AI prompt for question generation"""
        
        job_title = job_context.get("title", "Software Developer")
        required_skills = job_context.get("required_skills", [])
        experience_level = job_context.get("experience_level", "intermediate")
        
        category_guidance = {
            QuestionCategory.TECHNICAL: "Focus on technical skills, coding problems, and system design",
            QuestionCategory.BEHAVIORAL: "Focus on past experiences, teamwork, and problem-solving approaches",
            QuestionCategory.SITUATIONAL: "Focus on hypothetical scenarios and decision-making processes",
            QuestionCategory.COMPANY_CULTURE: "Focus on values, work style, and cultural fit",
            QuestionCategory.PROBLEM_SOLVING: "Focus on analytical thinking and problem-solving methodology"
        }
        
        prompt = f"""
        Generate {count} {category.value} interview questions for a {job_title} position.
        
        Job Context:
        - Experience Level: {experience_level}
        - Required Skills: {', '.join(required_skills[:5])}
        - Interview Type: {interview.interview_type}
        - Difficulty: {interview.difficulty_level}
        
        Category Guidance: {category_guidance.get(category, "")}
        
        For each question, provide:
        1. Question text (clear and specific)
        2. Expected answer approach (what to look for)
        3. Follow-up question suggestions
        4. Scoring criteria
        5. Expected duration in seconds
        
        Format as JSON array:
        [
            {{
                "question_text": "Your question here",
                "expected_approach": "What constitutes a good answer",
                "follow_up_suggestions": ["follow-up 1", "follow-up 2"],
                "scoring_criteria": ["criteria 1", "criteria 2"],
                "expected_duration": 120,
                "difficulty_level": "{interview.difficulty_level}",
                "skill_focus": ["skill1", "skill2"]
            }}
        ]
        
        Make questions specific to the role and avoid generic questions.
        """
        
        return prompt

    def _parse_ai_questions(self, response: str, category: QuestionCategory) -> List[Dict[str, Any]]:
        """Parse AI response into question format"""
        
        try:
            # Extract JSON from response
            import re
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                questions_data = json.loads(json_match.group())
                
                questions = []
                for q_data in questions_data:
                    question = {
                        "question_text": q_data.get("question_text", ""),
                        "category": category.value,
                        "expected_approach": q_data.get("expected_approach", ""),
                        "follow_up_suggestions": q_data.get("follow_up_suggestions", []),
                        "scoring_criteria": q_data.get("scoring_criteria", []),
                        "expected_duration": q_data.get("expected_duration", 120),
                        "difficulty_level": q_data.get("difficulty_level", "intermediate"),
                        "skill_focus": q_data.get("skill_focus", []),
                        "ai_generated": True,
                        "context_data": {
                            "generation_method": "ai",
                            "category": category.value
                        }
                    }
                    questions.append(question)
                
                return questions
        except Exception as e:
            logger.error(f"Error parsing AI questions: {e}")
        
        return []

    def _generate_template_questions(
        self,
        category: QuestionCategory,
        count: int,
        job_context: Dict
    ) -> List[Dict[str, Any]]:
        """Generate questions from templates when AI fails"""
        
        questions = []
        templates = self.question_pools.get(category, [])
        
        if not templates:
            # Fallback generic questions
            templates = [{
                "template": f"Tell me about your experience with {category.value} challenges.",
                "difficulty": QuestionDifficulty.INTERMEDIATE,
                "expected_duration": 120
            }]
        
        for i in range(count):
            template = random.choice(templates)
            
            # Fill template with job-specific content
            question_text = self._fill_template(template, job_context)
            
            question = {
                "question_text": question_text,
                "category": category.value,
                "expected_approach": f"Look for relevant experience and clear communication",
                "follow_up_suggestions": [
                    "Can you provide more details about that?",
                    "What would you do differently next time?"
                ],
                "scoring_criteria": ["Relevance", "Clarity", "Depth of experience"],
                "expected_duration": template.get("expected_duration", 120),
                "difficulty_level": template.get("difficulty", QuestionDifficulty.INTERMEDIATE).value,
                "skill_focus": [],
                "ai_generated": False,
                "context_data": {
                    "generation_method": "template",
                    "template_used": template.get("template", "")
                }
            }
            questions.append(question)
        
        return questions

    def _fill_template(self, template: Dict, job_context: Dict) -> str:
        """Fill question template with job-specific content"""
        
        question_template = template.get("template", "")
        
        # Replace placeholders with job-specific content
        if "{concept}" in question_template:
            concepts = template.get("concepts", ["programming concepts"])
            concept = random.choice(concepts)
            question_template = question_template.replace("{concept}", concept)
        
        if "{scenario}" in question_template:
            scenarios = template.get("scenarios", ["a technical problem"])
            scenario = random.choice(scenarios)
            question_template = question_template.replace("{scenario}", scenario)
        
        if "{situation}" in question_template:
            situations = template.get("situations", ["faced a challenge"])
            situation = random.choice(situations)
            question_template = question_template.replace("{situation}", situation)
        
        if "{task}" in question_template:
            tasks = template.get("tasks", ["completing a project"])
            task = random.choice(tasks)
            question_template = question_template.replace("{task}", task)
        
        if "{action}" in question_template:
            actions = template.get("actions", ["took initiative"])
            action = random.choice(actions)
            question_template = question_template.replace("{action}", action)
        
        return question_template

    def _extract_job_context(self, job_posting: JobPosting) -> Dict[str, Any]:
        """Extract relevant context from job posting"""
        
        context = {
            "title": job_posting.title,
            "experience_level": job_posting.experience_level,
            "required_skills": [skill.name for skill in job_posting.required_skills] if job_posting.required_skills else [],
            "department": job_posting.department,
            "job_type": job_posting.job_type,
            "description": job_posting.description[:500] if job_posting.description else "",
            "requirements": job_posting.requirements[:500] if job_posting.requirements else ""
        }
        
        return context

    def _apply_difficulty_progression(
        self, 
        questions: List[Dict[str, Any]], 
        base_difficulty: str
    ) -> List[Dict[str, Any]]:
        """Apply difficulty progression algorithm to questions"""
        
        if len(questions) <= 1:
            return questions
        
        # Define difficulty levels
        difficulty_levels = [
            QuestionDifficulty.BEGINNER,
            QuestionDifficulty.INTERMEDIATE, 
            QuestionDifficulty.ADVANCED,
            QuestionDifficulty.EXPERT
        ]
        
        base_index = difficulty_levels.index(QuestionDifficulty(base_difficulty))
        
        # Apply progression: start easier, gradually increase
        for i, question in enumerate(questions):
            progress_ratio = i / (len(questions) - 1) if len(questions) > 1 else 0
            
            # Calculate target difficulty index
            if i == 0:
                # Start one level below base (if possible)
                target_index = max(0, base_index - 1)
            elif i < len(questions) // 2:
                # First half: base difficulty
                target_index = base_index
            else:
                # Second half: gradually increase
                progression = int(progress_ratio * 2)  # 0 to 1 mapped to 0 to 2
                target_index = min(len(difficulty_levels) - 1, base_index + progression)
            
            question["difficulty_level"] = difficulty_levels[target_index].value
            
            # Adjust expected duration based on difficulty
            base_duration = question.get("expected_duration", 120)
            difficulty_multiplier = {
                QuestionDifficulty.BEGINNER: 0.8,
                QuestionDifficulty.INTERMEDIATE: 1.0,
                QuestionDifficulty.ADVANCED: 1.3,
                QuestionDifficulty.EXPERT: 1.6
            }
            
            multiplier = difficulty_multiplier.get(
                QuestionDifficulty(question["difficulty_level"]), 1.0
            )
            question["expected_duration"] = int(base_duration * multiplier)
        
        return questions

    async def _store_questions(
        self, 
        db: Session, 
        interview_id: str, 
        questions: List[Dict[str, Any]]
    ) -> None:
        """Store generated questions in database"""
        
        try:
            for question_data in questions:
                question = InterviewQuestion(
                    interview_id=interview_id,
                    question_text=question_data["question_text"],
                    category=question_data["category"],
                    difficulty_level=question_data["difficulty_level"],
                    expected_duration=question_data["expected_duration"],
                    question_order=question_data["question_order"],
                    is_follow_up=question_data.get("is_follow_up", False),
                    parent_question_id=question_data.get("parent_question_id"),
                    generated_from_job_requirements=question_data.get("ai_generated", False),
                    skill_focus=question_data.get("skill_focus", []),
                    context_data={
                        "expected_approach": question_data.get("expected_approach", ""),
                        "follow_up_suggestions": question_data.get("follow_up_suggestions", []),
                        "scoring_criteria": question_data.get("scoring_criteria", []),
                        **question_data.get("context_data", {})
                    }
                )
                db.add(question)
            
            db.commit()
            logger.info(f"Stored {len(questions)} questions for interview {interview_id}")
            
        except Exception as e:
            logger.error(f"Error storing questions: {e}")
            db.rollback()
            raise

    async def generate_follow_up_question(
        self,
        db: Session,
        parent_question_id: str,
        candidate_response: str,
        interview_context: Dict
    ) -> Optional[Dict[str, Any]]:
        """Generate follow-up question based on candidate response"""
        
        try:
            # Get parent question
            parent_question = db.query(InterviewQuestion).filter(
                InterviewQuestion.id == parent_question_id
            ).first()
            
            if not parent_question:
                return None
            
            # Generate follow-up using AI
            prompt = f"""
            Generate a follow-up question based on this interview exchange:
            
            Original Question: {parent_question.question_text}
            Candidate Response: {candidate_response}
            Question Category: {parent_question.category}
            
            Create a follow-up that:
            1. Digs deeper into their response
            2. Clarifies any unclear points
            3. Explores related aspects
            4. Maintains appropriate difficulty level
            
            Provide as JSON:
            {{
                "question_text": "Your follow-up question",
                "reasoning": "Why this follow-up is relevant",
                "expected_duration": 90
            }}
            """
            
            response = await self.ai_service._call_openai(prompt, max_tokens=500)
            follow_up_data = json.loads(response)
            
            # Create follow-up question
            follow_up = {
                "question_text": follow_up_data.get("question_text", "Can you elaborate on that?"),
                "category": parent_question.category,
                "difficulty_level": parent_question.difficulty_level,
                "expected_duration": follow_up_data.get("expected_duration", 90),
                "is_follow_up": True,
                "parent_question_id": parent_question_id,
                "ai_generated": True,
                "context_data": {
                    "generation_method": "follow_up",
                    "reasoning": follow_up_data.get("reasoning", ""),
                    "parent_response": candidate_response[:200]  # Store snippet
                }
            }
            
            return follow_up
            
        except Exception as e:
            logger.error(f"Error generating follow-up question: {e}")
            return None

    async def _generate_fallback_questions(
        self, 
        db: Session, 
        interview_id: str
    ) -> List[Dict[str, Any]]:
        """Generate basic fallback questions when all else fails"""
        
        fallback_questions = [
            {
                "question_text": "Tell me about yourself and your professional background.",
                "category": QuestionCategory.BEHAVIORAL.value,
                "difficulty_level": QuestionDifficulty.BEGINNER.value,
                "expected_duration": 120,
                "question_order": 1
            },
            {
                "question_text": "What interests you about this position?",
                "category": QuestionCategory.COMPANY_CULTURE.value,
                "difficulty_level": QuestionDifficulty.BEGINNER.value,
                "expected_duration": 90,
                "question_order": 2
            },
            {
                "question_text": "Describe a challenging project you've worked on recently.",
                "category": QuestionCategory.TECHNICAL.value,
                "difficulty_level": QuestionDifficulty.INTERMEDIATE.value,
                "expected_duration": 180,
                "question_order": 3
            }
        ]
        
        # Add metadata
        for question in fallback_questions:
            question.update({
                "interview_id": interview_id,
                "ai_generated": False,
                "is_follow_up": False,
                "parent_question_id": None,
                "skill_focus": [],
                "context_data": {"generation_method": "fallback"}
            })
        
        return fallback_questions

    def randomize_question_pool(
        self, 
        questions: List[Dict[str, Any]], 
        randomization_factor: float = 0.3
    ) -> List[Dict[str, Any]]:
        """Apply controlled randomization to question order"""
        
        if randomization_factor <= 0 or len(questions) <= 1:
            return questions
        
        # Group questions by category to maintain some structure
        categories = {}
        for question in questions:
            category = question.get("category", "general")
            if category not in categories:
                categories[category] = []
            categories[category].append(question)
        
        # Randomize within categories
        randomized_questions = []
        for category, category_questions in categories.items():
            if len(category_questions) > 1 and random.random() < randomization_factor:
                random.shuffle(category_questions)
            randomized_questions.extend(category_questions)
        
        # Update question order
        for i, question in enumerate(randomized_questions):
            question["question_order"] = i + 1
        
        return randomized_questions


# Create service instance
interview_question_service = InterviewQuestionService()