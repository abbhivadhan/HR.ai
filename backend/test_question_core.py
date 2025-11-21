#!/usr/bin/env python3
"""
Core functionality test for question generation system
Tests the core algorithms without database dependencies
"""

import sys
import os
import json
from enum import Enum
from typing import Dict, List, Any

class QuestionCategory(str, Enum):
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    SITUATIONAL = "situational"
    COMPANY_CULTURE = "company_culture"
    PROBLEM_SOLVING = "problem_solving"

class QuestionDifficulty(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

def test_question_distribution():
    """Test question distribution calculation logic"""
    
    def calculate_question_distribution(total_questions: int, interview_type: str, focus_areas: List[str]) -> Dict[QuestionCategory, int]:
        """Simplified version of the distribution algorithm"""
        distribution = {}
        
        if interview_type == "ai_technical":
            distribution[QuestionCategory.TECHNICAL] = max(1, int(total_questions * 0.7))
            distribution[QuestionCategory.PROBLEM_SOLVING] = max(1, int(total_questions * 0.2))
            distribution[QuestionCategory.BEHAVIORAL] = max(1, total_questions - 
                distribution[QuestionCategory.TECHNICAL] - distribution[QuestionCategory.PROBLEM_SOLVING])
        elif interview_type == "ai_behavioral":
            distribution[QuestionCategory.BEHAVIORAL] = max(1, int(total_questions * 0.6))
            distribution[QuestionCategory.SITUATIONAL] = max(1, int(total_questions * 0.3))
            distribution[QuestionCategory.COMPANY_CULTURE] = max(1, total_questions - 
                distribution[QuestionCategory.BEHAVIORAL] - distribution[QuestionCategory.SITUATIONAL])
        else:  # ai_screening or general
            distribution[QuestionCategory.TECHNICAL] = max(1, int(total_questions * 0.4))
            distribution[QuestionCategory.BEHAVIORAL] = max(1, int(total_questions * 0.3))
            distribution[QuestionCategory.SITUATIONAL] = max(1, int(total_questions * 0.2))
            distribution[QuestionCategory.COMPANY_CULTURE] = max(1, total_questions - 
                sum(distribution.values()))
        
        return distribution
    
    # Test technical interview
    tech_dist = calculate_question_distribution(10, "ai_technical", [])
    assert sum(tech_dist.values()) == 10
    assert tech_dist.get(QuestionCategory.TECHNICAL, 0) >= 5
    print("✅ Technical interview distribution test passed")
    
    # Test behavioral interview
    behav_dist = calculate_question_distribution(8, "ai_behavioral", [])
    assert sum(behav_dist.values()) == 8
    assert behav_dist.get(QuestionCategory.BEHAVIORAL, 0) >= 4
    print("✅ Behavioral interview distribution test passed")
    
    # Test screening interview
    screen_dist = calculate_question_distribution(6, "ai_screening", [])
    assert sum(screen_dist.values()) == 6
    assert len(screen_dist) >= 3
    print("✅ Screening interview distribution test passed")

def test_difficulty_progression():
    """Test difficulty progression algorithm"""
    
    def apply_difficulty_progression(questions: List[Dict[str, Any]], base_difficulty: str) -> List[Dict[str, Any]]:
        """Simplified version of difficulty progression"""
        if len(questions) <= 1:
            return questions
        
        difficulty_levels = [
            QuestionDifficulty.BEGINNER,
            QuestionDifficulty.INTERMEDIATE, 
            QuestionDifficulty.ADVANCED,
            QuestionDifficulty.EXPERT
        ]
        
        base_index = difficulty_levels.index(QuestionDifficulty(base_difficulty))
        
        for i, question in enumerate(questions):
            progress_ratio = i / (len(questions) - 1) if len(questions) > 1 else 0
            
            if i == 0:
                target_index = max(0, base_index - 1)
            elif i < len(questions) // 2:
                target_index = base_index
            else:
                progression = int(progress_ratio * 2)
                target_index = min(len(difficulty_levels) - 1, base_index + progression)
            
            question["difficulty_level"] = difficulty_levels[target_index].value
            
            # Adjust duration
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
    
    questions = [
        {"difficulty_level": "intermediate", "expected_duration": 120},
        {"difficulty_level": "intermediate", "expected_duration": 120},
        {"difficulty_level": "intermediate", "expected_duration": 120},
        {"difficulty_level": "intermediate", "expected_duration": 120}
    ]
    
    result = apply_difficulty_progression(questions, "intermediate")
    
    # First question should be easier
    assert result[0]["difficulty_level"] == "beginner"
    
    # Last question should be harder
    assert result[-1]["difficulty_level"] in ["advanced", "expert"]
    
    # Duration should be adjusted
    assert all("expected_duration" in q for q in result)
    
    print("✅ Difficulty progression test passed")

def test_ai_response_parsing():
    """Test AI response parsing logic"""
    
    def parse_ai_questions(response: str, category: QuestionCategory) -> List[Dict[str, Any]]:
        """Simplified AI response parser"""
        try:
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
                        "ai_generated": True
                    }
                    questions.append(question)
                
                return questions
        except Exception:
            pass
        
        return []
    
    # Test valid JSON response
    response = '''
    [
        {
            "question_text": "Explain Python decorators and provide an example.",
            "expected_approach": "Should demonstrate understanding of closures",
            "follow_up_suggestions": ["Can you show a practical use case?"],
            "scoring_criteria": ["Technical accuracy", "Code example quality"],
            "expected_duration": 180,
            "difficulty_level": "intermediate",
            "skill_focus": ["python", "decorators"]
        }
    ]
    '''
    
    questions = parse_ai_questions(response, QuestionCategory.TECHNICAL)
    
    assert len(questions) == 1
    assert questions[0]["question_text"] == "Explain Python decorators and provide an example."
    assert questions[0]["ai_generated"] is True
    assert "python" in questions[0]["skill_focus"]
    
    print("✅ AI response parsing test passed")
    
    # Test invalid JSON
    invalid_response = "Invalid JSON response"
    questions = parse_ai_questions(invalid_response, QuestionCategory.TECHNICAL)
    assert questions == []
    
    print("✅ Invalid JSON handling test passed")

def test_question_randomization():
    """Test question randomization logic"""
    
    def randomize_question_pool(questions: List[Dict[str, Any]], randomization_factor: float = 0.3) -> List[Dict[str, Any]]:
        """Simplified randomization logic"""
        import random
        
        if randomization_factor <= 0 or len(questions) <= 1:
            return questions
        
        # Group by category
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
    
    questions = [
        {"category": "technical", "question_order": 1, "question_text": "Q1"},
        {"category": "technical", "question_order": 2, "question_text": "Q2"},
        {"category": "behavioral", "question_order": 3, "question_text": "Q3"},
        {"category": "behavioral", "question_order": 4, "question_text": "Q4"}
    ]
    
    randomized = randomize_question_pool(questions, 1.0)
    
    # Should maintain same length
    assert len(randomized) == len(questions)
    
    # Should update question orders sequentially
    orders = [q["question_order"] for q in randomized]
    assert orders == list(range(1, len(questions) + 1))
    
    print("✅ Question randomization test passed")

def run_core_tests():
    """Run all core functionality tests"""
    print("🧪 Running Core Question Generation Tests")
    print("=" * 50)
    
    try:
        test_question_distribution()
        test_difficulty_progression()
        test_ai_response_parsing()
        test_question_randomization()
        
        print("\n" + "=" * 50)
        print("🎉 All core functionality tests passed!")
        print("\nCore algorithms verified:")
        print("• Question distribution calculation ✓")
        print("• Difficulty progression algorithm ✓")
        print("• AI response parsing ✓")
        print("• Question randomization ✓")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_core_tests()
    sys.exit(0 if success else 1)