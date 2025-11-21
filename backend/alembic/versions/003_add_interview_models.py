"""Add interview models

Revision ID: 003
Revises: 002
Create Date: 2024-01-03 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enums
    interview_type_enum = postgresql.ENUM('ai_screening', 'ai_technical', 'ai_behavioral', 'human_final', name='interviewtype')
    interview_type_enum.create(op.get_bind())
    
    interview_status_enum = postgresql.ENUM('scheduled', 'in_progress', 'completed', 'cancelled', 'no_show', 'technical_issues', name='interviewstatus')
    interview_status_enum.create(op.get_bind())
    
    session_status_enum = postgresql.ENUM('waiting', 'connecting', 'connected', 'recording', 'paused', 'ended', 'error', name='sessionstatus')
    session_status_enum.create(op.get_bind())
    
    question_category_enum = postgresql.ENUM('technical', 'behavioral', 'situational', 'company_culture', 'problem_solving', name='questioncategory')
    question_category_enum.create(op.get_bind())

    # Create interviews table
    op.create_table('interviews',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('job_application_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('candidate_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('interview_type', interview_type_enum, nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('scheduled_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('duration_minutes', sa.Integer(), nullable=True),
        sa.Column('timezone', sa.String(), nullable=True),
        sa.Column('status', interview_status_enum, nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('ai_interviewer_persona', sa.String(), nullable=True),
        sa.Column('difficulty_level', sa.String(), nullable=True),
        sa.Column('focus_areas', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('max_questions', sa.Integer(), nullable=True),
        sa.Column('allow_retakes', sa.Boolean(), nullable=True),
        sa.Column('recording_enabled', sa.Boolean(), nullable=True),
        sa.Column('overall_score', sa.Float(), nullable=True),
        sa.Column('recommendation', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['candidate_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['company_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['job_application_id'], ['job_applications.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_interviews_id'), 'interviews', ['id'], unique=False)
    op.create_index(op.f('ix_interviews_status'), 'interviews', ['status'], unique=False)

    # Create interview_sessions table
    op.create_table('interview_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('interview_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('session_token', sa.String(), nullable=False),
        sa.Column('room_id', sa.String(), nullable=False),
        sa.Column('status', session_status_enum, nullable=True),
        sa.Column('candidate_peer_id', sa.String(), nullable=True),
        sa.Column('ai_peer_id', sa.String(), nullable=True),
        sa.Column('signaling_server', sa.String(), nullable=True),
        sa.Column('joined_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_activity_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('connection_quality', sa.Float(), nullable=True),
        sa.Column('audio_quality', sa.Float(), nullable=True),
        sa.Column('video_quality', sa.Float(), nullable=True),
        sa.Column('latency_ms', sa.Integer(), nullable=True),
        sa.Column('recording_url', sa.String(), nullable=True),
        sa.Column('recording_duration', sa.Integer(), nullable=True),
        sa.Column('error_count', sa.Integer(), nullable=True),
        sa.Column('last_error', sa.Text(), nullable=True),
        sa.Column('reconnection_attempts', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['interview_id'], ['interviews.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_interview_sessions_id'), 'interview_sessions', ['id'], unique=False)
    op.create_index(op.f('ix_interview_sessions_session_token'), 'interview_sessions', ['session_token'], unique=True)
    op.create_index(op.f('ix_interview_sessions_room_id'), 'interview_sessions', ['room_id'], unique=True)
    op.create_index(op.f('ix_interview_sessions_status'), 'interview_sessions', ['status'], unique=False)

    # Create interview_analyses table
    op.create_table('interview_analyses',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('interview_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('overall_score', sa.Float(), nullable=False),
        sa.Column('technical_score', sa.Float(), nullable=True),
        sa.Column('communication_score', sa.Float(), nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=False),
        sa.Column('skill_scores', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('personality_traits', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('behavioral_indicators', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('speech_pace', sa.Float(), nullable=True),
        sa.Column('filler_word_count', sa.Integer(), nullable=True),
        sa.Column('clarity_score', sa.Float(), nullable=True),
        sa.Column('vocabulary_complexity', sa.Float(), nullable=True),
        sa.Column('emotion_timeline', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('engagement_score', sa.Float(), nullable=True),
        sa.Column('eye_contact_percentage', sa.Float(), nullable=True),
        sa.Column('gesture_analysis', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('questions_answered', sa.Integer(), nullable=True),
        sa.Column('average_response_time', sa.Float(), nullable=True),
        sa.Column('question_scores', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('strengths', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('areas_for_improvement', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('recommendations', sa.Text(), nullable=True),
        sa.Column('red_flags', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('analysis_confidence', sa.Float(), nullable=False),
        sa.Column('data_quality_score', sa.Float(), nullable=True),
        sa.Column('processed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('processing_duration', sa.Float(), nullable=True),
        sa.Column('ai_model_version', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['interview_id'], ['interviews.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('interview_id')
    )
    op.create_index(op.f('ix_interview_analyses_id'), 'interview_analyses', ['id'], unique=False)

    # Create interview_questions table
    op.create_table('interview_questions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('interview_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('question_text', sa.Text(), nullable=False),
        sa.Column('category', question_category_enum, nullable=False),
        sa.Column('difficulty_level', sa.String(), nullable=True),
        sa.Column('expected_duration', sa.Integer(), nullable=True),
        sa.Column('question_order', sa.Integer(), nullable=False),
        sa.Column('is_follow_up', sa.Boolean(), nullable=True),
        sa.Column('parent_question_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('generated_from_job_requirements', sa.Boolean(), nullable=True),
        sa.Column('skill_focus', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('context_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('candidate_response', sa.Text(), nullable=True),
        sa.Column('response_duration', sa.Float(), nullable=True),
        sa.Column('response_timestamp', sa.DateTime(timezone=True), nullable=True),
        sa.Column('response_score', sa.Float(), nullable=True),
        sa.Column('scoring_criteria', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('ai_feedback', sa.Text(), nullable=True),
        sa.Column('audio_analysis', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('video_analysis', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('asked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('answered_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['interview_id'], ['interviews.id'], ),
        sa.ForeignKeyConstraint(['parent_question_id'], ['interview_questions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_interview_questions_id'), 'interview_questions', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_interview_questions_id'), table_name='interview_questions')
    op.drop_table('interview_questions')
    op.drop_index(op.f('ix_interview_analyses_id'), table_name='interview_analyses')
    op.drop_table('interview_analyses')
    op.drop_index(op.f('ix_interview_sessions_status'), table_name='interview_sessions')
    op.drop_index(op.f('ix_interview_sessions_room_id'), table_name='interview_sessions')
    op.drop_index(op.f('ix_interview_sessions_session_token'), table_name='interview_sessions')
    op.drop_index(op.f('ix_interview_sessions_id'), table_name='interview_sessions')
    op.drop_table('interview_sessions')
    op.drop_index(op.f('ix_interviews_status'), table_name='interviews')
    op.drop_index(op.f('ix_interviews_id'), table_name='interviews')
    op.drop_table('interviews')
    
    # Drop enums
    question_category_enum = postgresql.ENUM('technical', 'behavioral', 'situational', 'company_culture', 'problem_solving', name='questioncategory')
    question_category_enum.drop(op.get_bind())
    
    session_status_enum = postgresql.ENUM('waiting', 'connecting', 'connected', 'recording', 'paused', 'ended', 'error', name='sessionstatus')
    session_status_enum.drop(op.get_bind())
    
    interview_status_enum = postgresql.ENUM('scheduled', 'in_progress', 'completed', 'cancelled', 'no_show', 'technical_issues', name='interviewstatus')
    interview_status_enum.drop(op.get_bind())
    
    interview_type_enum = postgresql.ENUM('ai_screening', 'ai_technical', 'ai_behavioral', 'human_final', name='interviewtype')
    interview_type_enum.drop(op.get_bind())