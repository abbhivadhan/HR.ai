"""Add assessment models

Revision ID: 002
Revises: 001
Create Date: 2024-01-02 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enums
    assessment_type_enum = postgresql.ENUM('technical', 'behavioral', 'cognitive', 'personality', 'coding', name='assessmenttype')
    assessment_type_enum.create(op.get_bind())
    
    question_type_enum = postgresql.ENUM('multiple_choice', 'coding', 'text_response', 'true_false', 'rating_scale', name='questiontype')
    question_type_enum.create(op.get_bind())
    
    difficulty_level_enum = postgresql.ENUM('beginner', 'intermediate', 'advanced', 'expert', name='difficultylevel')
    difficulty_level_enum.create(op.get_bind())
    
    assessment_status_enum = postgresql.ENUM('not_started', 'in_progress', 'completed', 'expired', 'cancelled', name='assessmentstatus')
    assessment_status_enum.create(op.get_bind())

    # Create questions table
    op.create_table('questions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('question_type', question_type_enum, nullable=False),
        sa.Column('difficulty_level', difficulty_level_enum, nullable=False),
        sa.Column('category', sa.String(), nullable=False),
        sa.Column('tags', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('options', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('correct_answer', sa.Text(), nullable=True),
        sa.Column('explanation', sa.Text(), nullable=True),
        sa.Column('code_template', sa.Text(), nullable=True),
        sa.Column('test_cases', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('max_points', sa.Float(), nullable=False),
        sa.Column('time_limit_seconds', sa.Integer(), nullable=True),
        sa.Column('ai_generated', sa.Boolean(), nullable=True),
        sa.Column('generation_prompt', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_questions_id'), 'questions', ['id'], unique=False)

    # Create assessments table
    op.create_table('assessments',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('candidate_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('job_posting_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('assessment_type', assessment_type_enum, nullable=False),
        sa.Column('status', assessment_status_enum, nullable=True),
        sa.Column('duration_minutes', sa.Integer(), nullable=False),
        sa.Column('total_questions', sa.Integer(), nullable=False),
        sa.Column('passing_score', sa.Float(), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('total_score', sa.Float(), nullable=True),
        sa.Column('percentage_score', sa.Float(), nullable=True),
        sa.Column('passed', sa.Boolean(), nullable=True),
        sa.Column('ai_analysis', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('skill_scores', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['candidate_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['job_posting_id'], ['job_postings.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_assessments_id'), 'assessments', ['id'], unique=False)

    # Create assessment_questions table
    op.create_table('assessment_questions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('assessment_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('question_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('order_index', sa.Integer(), nullable=False),
        sa.Column('points', sa.Float(), nullable=False),
        sa.Column('time_limit_seconds', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['assessment_id'], ['assessments.id'], ),
        sa.ForeignKeyConstraint(['question_id'], ['questions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create assessment_responses table
    op.create_table('assessment_responses',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('assessment_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('question_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('response_text', sa.Text(), nullable=True),
        sa.Column('selected_options', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('code_solution', sa.Text(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('time_spent_seconds', sa.Integer(), nullable=True),
        sa.Column('points_earned', sa.Float(), nullable=True),
        sa.Column('is_correct', sa.Boolean(), nullable=True),
        sa.Column('ai_feedback', sa.Text(), nullable=True),
        sa.Column('ai_score_breakdown', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['assessment_id'], ['assessments.id'], ),
        sa.ForeignKeyConstraint(['question_id'], ['questions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_assessment_responses_id'), 'assessment_responses', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_assessment_responses_id'), table_name='assessment_responses')
    op.drop_table('assessment_responses')
    op.drop_table('assessment_questions')
    op.drop_index(op.f('ix_assessments_id'), table_name='assessments')
    op.drop_table('assessments')
    op.drop_index(op.f('ix_questions_id'), table_name='questions')
    op.drop_table('questions')
    
    # Drop enums
    assessment_status_enum = postgresql.ENUM('not_started', 'in_progress', 'completed', 'expired', 'cancelled', name='assessmentstatus')
    assessment_status_enum.drop(op.get_bind())
    
    difficulty_level_enum = postgresql.ENUM('beginner', 'intermediate', 'advanced', 'expert', name='difficultylevel')
    difficulty_level_enum.drop(op.get_bind())
    
    question_type_enum = postgresql.ENUM('multiple_choice', 'coding', 'text_response', 'true_false', 'rating_scale', name='questiontype')
    question_type_enum.drop(op.get_bind())
    
    assessment_type_enum = postgresql.ENUM('technical', 'behavioral', 'cognitive', 'personality', 'coding', name='assessmenttype')
    assessment_type_enum.drop(op.get_bind())