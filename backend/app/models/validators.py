"""Model validation functions for interview system"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import re
import uuid


class InterviewValidationError(Exception):
    """Custom exception for interview validation errors"""
    pass


def validate_interview_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate interview creation/update data"""
    errors = []
    
    # Required fields
    required_fields = ['job_application_id', 'candidate_id', 'company_id', 'title', 'scheduled_at']
    for field in required_fields:
        if field not in data or data[field] is None:
            errors.append(f"{field} is required")
    
    # Validate UUIDs
    uuid_fields = ['job_application_id', 'candidate_id', 'company_id']
    for field in uuid_fields:
        if field in data and data[field]:
            try:
                uuid.UUID(str(data[field]))
            except (ValueError, TypeError):
                errors.append(f"{field} must be a valid UUID")
    
    # Validate scheduled_at is in the future
    if 'scheduled_at' in data and data['scheduled_at']:
        try:
            scheduled_time = data['scheduled_at']
            if isinstance(scheduled_time, str):
                scheduled_time = datetime.fromisoformat(scheduled_time.replace('Z', '+00:00'))
            
            if scheduled_time <= datetime.now(scheduled_time.tzinfo):
                errors.append("scheduled_at must be in the future")
        except (ValueError, TypeError):
            errors.append("scheduled_at must be a valid datetime")
    
    # Validate duration
    if 'duration_minutes' in data and data['duration_minutes'] is not None:
        duration = data['duration_minutes']
        if not isinstance(duration, int) or duration < 5 or duration > 180:
            errors.append("duration_minutes must be between 5 and 180 minutes")
    
    # Validate interview type
    valid_types = ['ai_screening', 'ai_technical', 'ai_behavioral', 'human_final']
    if 'interview_type' in data and data['interview_type'] not in valid_types:
        errors.append(f"interview_type must be one of: {', '.join(valid_types)}")
    
    # Validate difficulty level
    valid_difficulties = ['beginner', 'intermediate', 'advanced', 'expert']
    if 'difficulty_level' in data and data['difficulty_level'] and data['difficulty_level'] not in valid_difficulties:
        errors.append(f"difficulty_level must be one of: {', '.join(valid_difficulties)}")
    
    # Validate max_questions
    if 'max_questions' in data and data['max_questions'] is not None:
        max_q = data['max_questions']
        if not isinstance(max_q, int) or max_q < 1 or max_q > 50:
            errors.append("max_questions must be between 1 and 50")
    
    # Validate focus_areas
    if 'focus_areas' in data and data['focus_areas'] is not None:
        if not isinstance(data['focus_areas'], list):
            errors.append("focus_areas must be a list")
        elif len(data['focus_areas']) > 10:
            errors.append("focus_areas cannot have more than 10 items")
    
    if errors:
        raise InterviewValidationError("; ".join(errors))
    
    return data


def validate_session_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate interview session data"""
    errors = []
    
    # Required fields for session creation
    required_fields = ['interview_id']
    for field in required_fields:
        if field not in data or data[field] is None:
            errors.append(f"{field} is required")
    
    # Validate interview_id UUID
    if 'interview_id' in data and data['interview_id']:
        try:
            uuid.UUID(str(data['interview_id']))
        except (ValueError, TypeError):
            errors.append("interview_id must be a valid UUID")
    
    # Validate session_token format (if provided)
    if 'session_token' in data and data['session_token']:
        token = data['session_token']
        if not isinstance(token, str) or len(token) < 16 or len(token) > 128:
            errors.append("session_token must be a string between 16 and 128 characters")
    
    # Validate room_id format (if provided)
    if 'room_id' in data and data['room_id']:
        room_id = data['room_id']
        if not isinstance(room_id, str) or not re.match(r'^[a-zA-Z0-9_-]+$', room_id):
            errors.append("room_id must contain only alphanumeric characters, hyphens, and underscores")
    
    # Validate quality scores (0.0 to 1.0)
    quality_fields = ['connection_quality', 'audio_quality', 'video_quality']
    for field in quality_fields:
        if field in data and data[field] is not None:
            quality = data[field]
            if not isinstance(quality, (int, float)) or quality < 0.0 or quality > 1.0:
                errors.append(f"{field} must be a number between 0.0 and 1.0")
    
    # Validate latency
    if 'latency_ms' in data and data['latency_ms'] is not None:
        latency = data['latency_ms']
        if not isinstance(latency, int) or latency < 0 or latency > 10000:
            errors.append("latency_ms must be between 0 and 10000 milliseconds")
    
    # Validate recording duration
    if 'recording_duration' in data and data['recording_duration'] is not None:
        duration = data['recording_duration']
        if not isinstance(duration, int) or duration < 0:
            errors.append("recording_duration must be a non-negative integer")
    
    if errors:
        raise InterviewValidationError("; ".join(errors))
    
    return data


def validate_analysis_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate interview analysis data"""
    errors = []
    
    # Required fields
    required_fields = ['interview_id', 'overall_score', 'communication_score', 'confidence_score', 'analysis_confidence']
    for field in required_fields:
        if field not in data or data[field] is None:
            errors.append(f"{field} is required")
    
    # Validate interview_id UUID
    if 'interview_id' in data and data['interview_id']:
        try:
            uuid.UUID(str(data['interview_id']))
        except (ValueError, TypeError):
            errors.append("interview_id must be a valid UUID")
    
    # Validate score fields (0.0 to 1.0)
    score_fields = [
        'overall_score', 'technical_score', 'communication_score', 'confidence_score',
        'clarity_score', 'engagement_score', 'eye_contact_percentage', 'analysis_confidence',
        'data_quality_score'
    ]
    for field in score_fields:
        if field in data and data[field] is not None:
            score = data[field]
            if not isinstance(score, (int, float)) or score < 0.0 or score > 1.0:
                errors.append(f"{field} must be a number between 0.0 and 1.0")
    
    # Validate speech pace (words per minute)
    if 'speech_pace' in data and data['speech_pace'] is not None:
        pace = data['speech_pace']
        if not isinstance(pace, (int, float)) or pace < 0 or pace > 500:
            errors.append("speech_pace must be between 0 and 500 words per minute")
    
    # Validate filler word count
    if 'filler_word_count' in data and data['filler_word_count'] is not None:
        count = data['filler_word_count']
        if not isinstance(count, int) or count < 0:
            errors.append("filler_word_count must be a non-negative integer")
    
    # Validate questions answered
    if 'questions_answered' in data and data['questions_answered'] is not None:
        count = data['questions_answered']
        if not isinstance(count, int) or count < 0:
            errors.append("questions_answered must be a non-negative integer")
    
    # Validate average response time
    if 'average_response_time' in data and data['average_response_time'] is not None:
        time = data['average_response_time']
        if not isinstance(time, (int, float)) or time < 0:
            errors.append("average_response_time must be a non-negative number")
    
    # Validate JSON fields structure
    json_fields = ['skill_scores', 'personality_traits', 'behavioral_indicators', 'emotion_timeline', 'gesture_analysis', 'question_scores']
    for field in json_fields:
        if field in data and data[field] is not None:
            if not isinstance(data[field], dict):
                errors.append(f"{field} must be a dictionary/object")
    
    # Validate array fields
    array_fields = ['strengths', 'areas_for_improvement', 'red_flags']
    for field in array_fields:
        if field in data and data[field] is not None:
            if not isinstance(data[field], list):
                errors.append(f"{field} must be a list")
            elif len(data[field]) > 20:
                errors.append(f"{field} cannot have more than 20 items")
    
    # Validate processing duration
    if 'processing_duration' in data and data['processing_duration'] is not None:
        duration = data['processing_duration']
        if not isinstance(duration, (int, float)) or duration < 0:
            errors.append("processing_duration must be a non-negative number")
    
    if errors:
        raise InterviewValidationError("; ".join(errors))
    
    return data


def validate_question_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate interview question data"""
    errors = []
    
    # Required fields
    required_fields = ['interview_id', 'question_text', 'category', 'question_order']
    for field in required_fields:
        if field not in data or data[field] is None:
            errors.append(f"{field} is required")
    
    # Validate interview_id UUID
    if 'interview_id' in data and data['interview_id']:
        try:
            uuid.UUID(str(data['interview_id']))
        except (ValueError, TypeError):
            errors.append("interview_id must be a valid UUID")
    
    # Validate parent_question_id UUID (if provided)
    if 'parent_question_id' in data and data['parent_question_id']:
        try:
            uuid.UUID(str(data['parent_question_id']))
        except (ValueError, TypeError):
            errors.append("parent_question_id must be a valid UUID")
    
    # Validate question text length
    if 'question_text' in data and data['question_text']:
        text = data['question_text']
        if not isinstance(text, str) or len(text.strip()) < 10 or len(text) > 2000:
            errors.append("question_text must be between 10 and 2000 characters")
    
    # Validate category
    valid_categories = ['technical', 'behavioral', 'situational', 'company_culture', 'problem_solving']
    if 'category' in data and data['category'] not in valid_categories:
        errors.append(f"category must be one of: {', '.join(valid_categories)}")
    
    # Validate difficulty level
    valid_difficulties = ['beginner', 'intermediate', 'advanced', 'expert']
    if 'difficulty_level' in data and data['difficulty_level'] and data['difficulty_level'] not in valid_difficulties:
        errors.append(f"difficulty_level must be one of: {', '.join(valid_difficulties)}")
    
    # Validate expected duration
    if 'expected_duration' in data and data['expected_duration'] is not None:
        duration = data['expected_duration']
        if not isinstance(duration, int) or duration < 10 or duration > 1800:
            errors.append("expected_duration must be between 10 and 1800 seconds")
    
    # Validate question order
    if 'question_order' in data and data['question_order'] is not None:
        order = data['question_order']
        if not isinstance(order, int) or order < 1:
            errors.append("question_order must be a positive integer")
    
    # Validate response duration
    if 'response_duration' in data and data['response_duration'] is not None:
        duration = data['response_duration']
        if not isinstance(duration, (int, float)) or duration < 0:
            errors.append("response_duration must be a non-negative number")
    
    # Validate response score
    if 'response_score' in data and data['response_score'] is not None:
        score = data['response_score']
        if not isinstance(score, (int, float)) or score < 0.0 or score > 1.0:
            errors.append("response_score must be between 0.0 and 1.0")
    
    # Validate skill focus array
    if 'skill_focus' in data and data['skill_focus'] is not None:
        if not isinstance(data['skill_focus'], list):
            errors.append("skill_focus must be a list")
        elif len(data['skill_focus']) > 10:
            errors.append("skill_focus cannot have more than 10 items")
    
    # Validate JSON fields
    json_fields = ['context_data', 'scoring_criteria', 'audio_analysis', 'video_analysis']
    for field in json_fields:
        if field in data and data[field] is not None:
            if not isinstance(data[field], dict):
                errors.append(f"{field} must be a dictionary/object")
    
    if errors:
        raise InterviewValidationError("; ".join(errors))
    
    return data


def validate_session_status_transition(current_status: str, new_status: str) -> bool:
    """Validate if a session status transition is allowed"""
    valid_transitions = {
        'waiting': ['connecting', 'cancelled', 'error'],
        'connecting': ['connected', 'error', 'cancelled'],
        'connected': ['recording', 'paused', 'ended', 'error'],
        'recording': ['paused', 'ended', 'error'],
        'paused': ['recording', 'ended', 'error'],
        'ended': [],  # Terminal state
        'error': ['connecting', 'ended', 'cancelled']  # Can retry or end
    }
    
    return new_status in valid_transitions.get(current_status, [])


def validate_interview_status_transition(current_status: str, new_status: str) -> bool:
    """Validate if an interview status transition is allowed"""
    valid_transitions = {
        'scheduled': ['in_progress', 'cancelled', 'no_show', 'technical_issues'],
        'in_progress': ['completed', 'cancelled', 'technical_issues'],
        'completed': [],  # Terminal state
        'cancelled': [],  # Terminal state
        'no_show': ['scheduled'],  # Can reschedule
        'technical_issues': ['scheduled', 'cancelled']  # Can reschedule or cancel
    }
    
    return new_status in valid_transitions.get(current_status, [])