#!/usr/bin/env python3
"""
Test script to validate interview model definitions and relationships
"""
import sys
import os
from datetime import datetime, timedelta
import uuid

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

try:
    from app.models.interview import (
        Interview, InterviewSession, InterviewAnalysis, InterviewQuestion,
        InterviewType, InterviewStatus, SessionStatus, QuestionCategory
    )
    from app.models.validators import (
        validate_interview_data, validate_session_data, validate_analysis_data,
        validate_question_data, validate_session_status_transition,
        validate_interview_status_transition, InterviewValidationError
    )
    print("✅ Successfully imported all interview models and validators")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def test_enum_values():
    """Test that all enum values are correctly defined"""
    print("\n🧪 Testing enum values...")
    
    # Test InterviewType enum
    expected_interview_types = ['ai_screening', 'ai_technical', 'ai_behavioral', 'human_final']
    for interview_type in expected_interview_types:
        assert hasattr(InterviewType, interview_type.upper())
        print(f"  ✅ InterviewType.{interview_type.upper()} = {getattr(InterviewType, interview_type.upper())}")
    
    # Test InterviewStatus enum
    expected_interview_statuses = ['scheduled', 'in_progress', 'completed', 'cancelled', 'no_show', 'technical_issues']
    for status in expected_interview_statuses:
        assert hasattr(InterviewStatus, status.upper())
        print(f"  ✅ InterviewStatus.{status.upper()} = {getattr(InterviewStatus, status.upper())}")
    
    # Test SessionStatus enum
    expected_session_statuses = ['waiting', 'connecting', 'connected', 'recording', 'paused', 'ended', 'error']
    for status in expected_session_statuses:
        assert hasattr(SessionStatus, status.upper())
        print(f"  ✅ SessionStatus.{status.upper()} = {getattr(SessionStatus, status.upper())}")
    
    # Test QuestionCategory enum
    expected_categories = ['technical', 'behavioral', 'situational', 'company_culture', 'problem_solving']
    for category in expected_categories:
        assert hasattr(QuestionCategory, category.upper())
        print(f"  ✅ QuestionCategory.{category.upper()} = {getattr(QuestionCategory, category.upper())}")

def test_model_attributes():
    """Test that all models have the expected attributes"""
    print("\n🧪 Testing model attributes...")
    
    # Test Interview model attributes
    interview_attrs = [
        'id', 'job_application_id', 'candidate_id', 'company_id', 'interview_type',
        'title', 'description', 'scheduled_at', 'duration_minutes', 'timezone',
        'status', 'started_at', 'completed_at', 'ai_interviewer_persona',
        'difficulty_level', 'focus_areas', 'max_questions', 'allow_retakes',
        'recording_enabled', 'overall_score', 'recommendation', 'created_at', 'updated_at'
    ]
    
    for attr in interview_attrs:
        assert hasattr(Interview, attr), f"Interview model missing attribute: {attr}"
    print(f"  ✅ Interview model has all {len(interview_attrs)} expected attributes")
    
    # Test InterviewSession model attributes
    session_attrs = [
        'id', 'interview_id', 'session_token', 'room_id', 'status',
        'candidate_peer_id', 'ai_peer_id', 'signaling_server', 'joined_at',
        'started_at', 'ended_at', 'last_activity_at', 'connection_quality',
        'audio_quality', 'video_quality', 'latency_ms', 'recording_url',
        'recording_duration', 'error_count', 'last_error', 'reconnection_attempts',
        'created_at', 'updated_at'
    ]
    
    for attr in session_attrs:
        assert hasattr(InterviewSession, attr), f"InterviewSession model missing attribute: {attr}"
    print(f"  ✅ InterviewSession model has all {len(session_attrs)} expected attributes")
    
    # Test InterviewAnalysis model attributes
    analysis_attrs = [
        'id', 'interview_id', 'overall_score', 'technical_score', 'communication_score',
        'confidence_score', 'skill_scores', 'personality_traits', 'behavioral_indicators',
        'speech_pace', 'filler_word_count', 'clarity_score', 'vocabulary_complexity',
        'emotion_timeline', 'engagement_score', 'eye_contact_percentage', 'gesture_analysis',
        'questions_answered', 'average_response_time', 'question_scores', 'strengths',
        'areas_for_improvement', 'recommendations', 'red_flags', 'analysis_confidence',
        'data_quality_score', 'processed_at', 'processing_duration', 'ai_model_version',
        'created_at', 'updated_at'
    ]
    
    for attr in analysis_attrs:
        assert hasattr(InterviewAnalysis, attr), f"InterviewAnalysis model missing attribute: {attr}"
    print(f"  ✅ InterviewAnalysis model has all {len(analysis_attrs)} expected attributes")
    
    # Test InterviewQuestion model attributes
    question_attrs = [
        'id', 'interview_id', 'question_text', 'category', 'difficulty_level',
        'expected_duration', 'question_order', 'is_follow_up', 'parent_question_id',
        'generated_from_job_requirements', 'skill_focus', 'context_data',
        'candidate_response', 'response_duration', 'response_timestamp',
        'response_score', 'scoring_criteria', 'ai_feedback', 'audio_analysis',
        'video_analysis', 'asked_at', 'answered_at', 'created_at'
    ]
    
    for attr in question_attrs:
        assert hasattr(InterviewQuestion, attr), f"InterviewQuestion model missing attribute: {attr}"
    print(f"  ✅ InterviewQuestion model has all {len(question_attrs)} expected attributes")

def test_validators():
    """Test validation functions"""
    print("\n🧪 Testing validation functions...")
    
    # Test valid interview data
    valid_interview_data = {
        'job_application_id': str(uuid.uuid4()),
        'candidate_id': str(uuid.uuid4()),
        'company_id': str(uuid.uuid4()),
        'title': 'Technical Interview',
        'scheduled_at': datetime.now() + timedelta(hours=1),
        'duration_minutes': 60,
        'interview_type': 'ai_technical',
        'difficulty_level': 'intermediate',
        'max_questions': 10,
        'focus_areas': ['python', 'algorithms']
    }
    
    try:
        validated_data = validate_interview_data(valid_interview_data)
        print("  ✅ Valid interview data passed validation")
    except InterviewValidationError as e:
        print(f"  ❌ Valid interview data failed validation: {e}")
        return False
    
    # Test invalid interview data
    invalid_interview_data = {
        'job_application_id': 'invalid-uuid',
        'title': 'Test',
        'scheduled_at': datetime.now() - timedelta(hours=1),  # Past date
        'duration_minutes': 300,  # Too long
        'max_questions': 100  # Too many
    }
    
    try:
        validate_interview_data(invalid_interview_data)
        print("  ❌ Invalid interview data should have failed validation")
        return False
    except InterviewValidationError:
        print("  ✅ Invalid interview data correctly failed validation")
    
    # Test session status transitions
    valid_transitions = [
        ('waiting', 'connecting'),
        ('connecting', 'connected'),
        ('connected', 'recording'),
        ('recording', 'ended')
    ]
    
    for current, new in valid_transitions:
        if validate_session_status_transition(current, new):
            print(f"  ✅ Valid transition: {current} -> {new}")
        else:
            print(f"  ❌ Valid transition failed: {current} -> {new}")
            return False
    
    # Test invalid session status transition
    if not validate_session_status_transition('ended', 'connecting'):
        print("  ✅ Invalid transition correctly rejected: ended -> connecting")
    else:
        print("  ❌ Invalid transition should have been rejected: ended -> connecting")
        return False
    
    return True

def test_model_relationships():
    """Test that model relationships are properly defined"""
    print("\n🧪 Testing model relationships...")
    
    # Check Interview relationships
    interview_relationships = ['job_application', 'candidate', 'company', 'sessions', 'analysis']
    for rel in interview_relationships:
        assert hasattr(Interview, rel), f"Interview model missing relationship: {rel}"
    print(f"  ✅ Interview model has all {len(interview_relationships)} expected relationships")
    
    # Check InterviewSession relationships
    session_relationships = ['interview']
    for rel in session_relationships:
        assert hasattr(InterviewSession, rel), f"InterviewSession model missing relationship: {rel}"
    print(f"  ✅ InterviewSession model has all {len(session_relationships)} expected relationships")
    
    # Check InterviewAnalysis relationships
    analysis_relationships = ['interview']
    for rel in analysis_relationships:
        assert hasattr(InterviewAnalysis, rel), f"InterviewAnalysis model missing relationship: {rel}"
    print(f"  ✅ InterviewAnalysis model has all {len(analysis_relationships)} expected relationships")
    
    # Check InterviewQuestion relationships
    question_relationships = ['interview', 'follow_up_questions']
    for rel in question_relationships:
        assert hasattr(InterviewQuestion, rel), f"InterviewQuestion model missing relationship: {rel}"
    print(f"  ✅ InterviewQuestion model has all {len(question_relationships)} expected relationships")

def main():
    """Run all tests"""
    print("🚀 Starting interview models validation tests...")
    
    try:
        test_enum_values()
        test_model_attributes()
        test_model_relationships()
        
        if test_validators():
            print("\n🎉 All tests passed! Interview models are properly defined.")
            return True
        else:
            print("\n❌ Some validation tests failed.")
            return False
            
    except Exception as e:
        print(f"\n💥 Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)