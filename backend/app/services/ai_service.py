import openai
import json
import re
from typing import List, Dict, Any, Optional
from ..models.assessment import QuestionType, DifficultyLevel
from ..schemas.assessment import GenerateQuestionsRequest, AIAnalysisResult
from ..config import settings


class AIService:
    def __init__(self):
        # Initialize OpenAI client (you'll need to add OPENAI_API_KEY to config)
        self.client = openai.OpenAI(api_key=getattr(settings, 'openai_api_key', None))
    
    async def generate_questions(self, request: GenerateQuestionsRequest) -> List[Dict[str, Any]]:
        """Generate questions using AI based on job requirements"""
        
        prompt = self._build_question_generation_prompt(request)
        
        try:
            response = await self._call_openai(prompt, max_tokens=2000)
            questions = self._parse_generated_questions(response, request)
            return questions
        except Exception as e:
            # Fallback to template questions if AI fails
            return self._get_fallback_questions(request)
    
    async def evaluate_response(self, 
                              question: Dict[str, Any], 
                              response: str, 
                              question_type: QuestionType) -> Dict[str, Any]:
        """Evaluate a candidate's response using AI"""
        
        if question_type == QuestionType.MULTIPLE_CHOICE:
            return self._evaluate_multiple_choice(question, response)
        elif question_type == QuestionType.CODING:
            return await self._evaluate_coding_response(question, response)
        elif question_type == QuestionType.TEXT_RESPONSE:
            return await self._evaluate_text_response(question, response)
        else:
            return self._evaluate_basic_response(question, response)
    
    async def analyze_assessment_results(self, 
                                       responses: List[Dict[str, Any]], 
                                       questions: List[Dict[str, Any]]) -> AIAnalysisResult:
        """Perform comprehensive AI analysis of assessment results"""
        
        # Calculate skill breakdown
        skill_scores = self._calculate_skill_scores(responses, questions)
        
        # Generate AI insights
        prompt = self._build_analysis_prompt(responses, questions, skill_scores)
        
        try:
            ai_response = await self._call_openai(prompt, max_tokens=1000)
            analysis = self._parse_analysis_response(ai_response, skill_scores)
            return analysis
        except Exception as e:
            # Fallback analysis
            return self._generate_fallback_analysis(skill_scores)
    
    def _build_question_generation_prompt(self, request: GenerateQuestionsRequest) -> str:
        """Build prompt for question generation"""
        
        question_types_str = ", ".join([qt.value for qt in request.question_types])
        skills_str = ", ".join(request.required_skills)
        
        prompt = f"""
        Generate {request.question_count} {request.difficulty_level.value} level interview questions for a {request.job_title} position.
        
        Required skills to focus on: {skills_str}
        Question types to include: {question_types_str}
        Difficulty level: {request.difficulty_level.value}
        
        For each question, provide:
        1. Title (brief description)
        2. Content (the actual question)
        3. Question type
        4. Category (main skill being tested)
        5. Tags (specific topics)
        6. For multiple choice: 4 options with correct answer
        7. For coding: test cases and expected solution approach
        8. Explanation of the correct answer
        9. Points (1-20 based on difficulty)
        
        Format as JSON array with this structure:
        [
            {{
                "title": "Question title",
                "content": "Question content",
                "question_type": "multiple_choice|coding|text_response",
                "category": "skill_name",
                "tags": ["tag1", "tag2"],
                "options": {{"A": "option1", "B": "option2", "C": "option3", "D": "option4"}},
                "correct_answer": "B",
                "explanation": "Why this is correct",
                "max_points": 10,
                "test_cases": [/* for coding questions */]
            }}
        ]
        """
        
        return prompt
    
    def _build_analysis_prompt(self, responses: List[Dict], questions: List[Dict], skill_scores: Dict[str, float]) -> str:
        """Build prompt for assessment analysis"""
        
        response_summary = []
        for i, (response, question) in enumerate(zip(responses, questions)):
            response_summary.append(f"Q{i+1} ({question['category']}): {response.get('points_earned', 0)}/{question['max_points']} points")
        
        prompt = f"""
        Analyze this candidate's assessment performance and provide insights:
        
        Skill Scores: {json.dumps(skill_scores, indent=2)}
        
        Question Performance:
        {chr(10).join(response_summary)}
        
        Provide analysis in this JSON format:
        {{
            "overall_score": 0-100,
            "strengths": ["strength1", "strength2"],
            "weaknesses": ["weakness1", "weakness2"], 
            "recommendations": ["recommendation1", "recommendation2"],
            "confidence_level": 0.0-1.0
        }}
        
        Focus on:
        1. Technical competency assessment
        2. Areas for improvement
        3. Specific learning recommendations
        4. Overall hiring recommendation confidence
        """
        
        return prompt
    
    async def _call_openai(self, prompt: str, max_tokens: int = 1000) -> str:
        """Make API call to OpenAI"""
        
        if not self.client.api_key:
            raise Exception("OpenAI API key not configured")
        
        response = await self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert technical interviewer and assessment creator."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    
    def _parse_generated_questions(self, response: str, request: GenerateQuestionsRequest) -> List[Dict[str, Any]]:
        """Parse AI response into question format"""
        
        try:
            # Extract JSON from response
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                questions_data = json.loads(json_match.group())
                
                # Validate and format questions
                questions = []
                for q_data in questions_data:
                    question = {
                        "title": q_data.get("title", "Generated Question"),
                        "content": q_data.get("content", ""),
                        "question_type": q_data.get("question_type", "multiple_choice"),
                        "difficulty_level": request.difficulty_level.value,
                        "category": q_data.get("category", request.required_skills[0] if request.required_skills else "general"),
                        "tags": q_data.get("tags", []),
                        "options": q_data.get("options"),
                        "correct_answer": q_data.get("correct_answer"),
                        "explanation": q_data.get("explanation"),
                        "max_points": q_data.get("max_points", 10),
                        "test_cases": q_data.get("test_cases"),
                        "ai_generated": True,
                        "generation_prompt": f"Generated for {request.job_title} position"
                    }
                    questions.append(question)
                
                return questions[:request.question_count]
        except Exception as e:
            pass
        
        return self._get_fallback_questions(request)
    
    def _get_fallback_questions(self, request: GenerateQuestionsRequest) -> List[Dict[str, Any]]:
        """Provide fallback questions when AI generation fails"""
        
        fallback_questions = [
            {
                "title": "Problem Solving Approach",
                "content": "Describe your approach to solving complex technical problems.",
                "question_type": "text_response",
                "difficulty_level": request.difficulty_level.value,
                "category": "problem_solving",
                "tags": ["analytical_thinking", "methodology"],
                "max_points": 15,
                "ai_generated": False
            },
            {
                "title": "Technical Experience",
                "content": f"What experience do you have with {request.required_skills[0] if request.required_skills else 'relevant technologies'}?",
                "question_type": "text_response", 
                "difficulty_level": request.difficulty_level.value,
                "category": request.required_skills[0] if request.required_skills else "general",
                "tags": ["experience", "technical_skills"],
                "max_points": 10,
                "ai_generated": False
            }
        ]
        
        return fallback_questions[:request.question_count]
    
    def _evaluate_multiple_choice(self, question: Dict, response: str) -> Dict[str, Any]:
        """Evaluate multiple choice response"""
        
        correct_answer = question.get("correct_answer", "")
        is_correct = response.strip().upper() == correct_answer.strip().upper()
        
        points_earned = question.get("max_points", 10) if is_correct else 0
        
        return {
            "points_earned": points_earned,
            "is_correct": is_correct,
            "ai_feedback": question.get("explanation", ""),
            "ai_score_breakdown": {
                "accuracy": 1.0 if is_correct else 0.0,
                "confidence": 1.0
            }
        }
    
    async def _evaluate_coding_response(self, question: Dict, response: str) -> Dict[str, Any]:
        """Evaluate coding response using AI"""
        
        prompt = f"""
        Evaluate this coding solution:
        
        Question: {question.get('content', '')}
        Expected approach: {question.get('explanation', '')}
        Candidate solution: {response}
        Test cases: {json.dumps(question.get('test_cases', []))}
        
        Provide evaluation as JSON:
        {{
            "correctness": 0.0-1.0,
            "code_quality": 0.0-1.0,
            "efficiency": 0.0-1.0,
            "overall_score": 0.0-1.0,
            "feedback": "detailed feedback"
        }}
        """
        
        try:
            ai_response = await self._call_openai(prompt, max_tokens=500)
            evaluation = json.loads(ai_response)
            
            max_points = question.get("max_points", 20)
            points_earned = max_points * evaluation.get("overall_score", 0.5)
            
            return {
                "points_earned": points_earned,
                "is_correct": evaluation.get("overall_score", 0) >= 0.7,
                "ai_feedback": evaluation.get("feedback", ""),
                "ai_score_breakdown": evaluation
            }
        except Exception:
            # Fallback evaluation
            return {
                "points_earned": question.get("max_points", 20) * 0.5,
                "is_correct": len(response.strip()) > 50,  # Basic check
                "ai_feedback": "Code solution provided",
                "ai_score_breakdown": {"overall_score": 0.5}
            }
    
    async def _evaluate_text_response(self, question: Dict, response: str) -> Dict[str, Any]:
        """Evaluate text response using AI"""
        
        prompt = f"""
        Evaluate this text response:
        
        Question: {question.get('content', '')}
        Response: {response}
        
        Rate on scale 0.0-1.0 for:
        - Relevance to question
        - Technical accuracy
        - Depth of knowledge
        - Communication clarity
        
        Provide as JSON:
        {{
            "relevance": 0.0-1.0,
            "accuracy": 0.0-1.0,
            "depth": 0.0-1.0,
            "clarity": 0.0-1.0,
            "overall_score": 0.0-1.0,
            "feedback": "constructive feedback"
        }}
        """
        
        try:
            ai_response = await self._call_openai(prompt, max_tokens=300)
            evaluation = json.loads(ai_response)
            
            max_points = question.get("max_points", 15)
            points_earned = max_points * evaluation.get("overall_score", 0.6)
            
            return {
                "points_earned": points_earned,
                "is_correct": evaluation.get("overall_score", 0) >= 0.6,
                "ai_feedback": evaluation.get("feedback", ""),
                "ai_score_breakdown": evaluation
            }
        except Exception:
            # Fallback evaluation
            word_count = len(response.split())
            score = min(1.0, word_count / 50)  # Basic scoring by length
            
            return {
                "points_earned": question.get("max_points", 15) * score,
                "is_correct": word_count >= 20,
                "ai_feedback": "Response evaluated based on completeness",
                "ai_score_breakdown": {"overall_score": score}
            }
    
    def _evaluate_basic_response(self, question: Dict, response: str) -> Dict[str, Any]:
        """Basic evaluation for other question types"""
        
        has_response = bool(response and response.strip())
        points_earned = question.get("max_points", 10) * (0.8 if has_response else 0)
        
        return {
            "points_earned": points_earned,
            "is_correct": has_response,
            "ai_feedback": "Response provided" if has_response else "No response given",
            "ai_score_breakdown": {"completion": 1.0 if has_response else 0.0}
        }
    
    def _calculate_skill_scores(self, responses: List[Dict], questions: List[Dict]) -> Dict[str, float]:
        """Calculate scores by skill category"""
        
        skill_totals = {}
        skill_maxes = {}
        
        for response, question in zip(responses, questions):
            category = question.get("category", "general")
            points_earned = response.get("points_earned", 0)
            max_points = question.get("max_points", 10)
            
            if category not in skill_totals:
                skill_totals[category] = 0
                skill_maxes[category] = 0
            
            skill_totals[category] += points_earned
            skill_maxes[category] += max_points
        
        skill_scores = {}
        for skill in skill_totals:
            if skill_maxes[skill] > 0:
                skill_scores[skill] = (skill_totals[skill] / skill_maxes[skill]) * 100
            else:
                skill_scores[skill] = 0
        
        return skill_scores
    
    def _parse_analysis_response(self, response: str, skill_scores: Dict[str, float]) -> AIAnalysisResult:
        """Parse AI analysis response"""
        
        try:
            analysis_data = json.loads(response)
            
            return AIAnalysisResult(
                overall_score=analysis_data.get("overall_score", sum(skill_scores.values()) / len(skill_scores) if skill_scores else 0),
                skill_breakdown=skill_scores,
                strengths=analysis_data.get("strengths", []),
                weaknesses=analysis_data.get("weaknesses", []),
                recommendations=analysis_data.get("recommendations", []),
                confidence_level=analysis_data.get("confidence_level", 0.7)
            )
        except Exception:
            return self._generate_fallback_analysis(skill_scores)
    
    def _generate_fallback_analysis(self, skill_scores: Dict[str, float]) -> AIAnalysisResult:
        """Generate fallback analysis when AI fails"""
        
        overall_score = sum(skill_scores.values()) / len(skill_scores) if skill_scores else 0
        
        # Simple rule-based analysis
        strengths = [skill for skill, score in skill_scores.items() if score >= 80]
        weaknesses = [skill for skill, score in skill_scores.items() if score < 60]
        
        recommendations = []
        for weakness in weaknesses:
            recommendations.append(f"Improve {weakness} skills through practice and study")
        
        return AIAnalysisResult(
            overall_score=overall_score,
            skill_breakdown=skill_scores,
            strengths=strengths or ["Problem solving approach"],
            weaknesses=weaknesses or ["Areas for improvement identified"],
            recommendations=recommendations or ["Continue developing technical skills"],
            confidence_level=0.6
        )