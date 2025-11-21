"""Add job matching models

Revision ID: 004_add_job_matching_models
Revises: 003_add_interview_models
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '004_add_job_matching_models'
down_revision = '003_add_interview_models'
branch_labels = None
depends_on = None


def upgrade():
    # Create job_match_scores table
    op.create_table('job_match_scores',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('candidate_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('job_posting_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('overall_score', sa.Float(), nullable=False),
        sa.Column('skill_match_score', sa.Float(), nullable=True),
        sa.Column('experience_match_score', sa.Float(), nullable=True),
        sa.Column('location_match_score', sa.Float(), nullable=True),
        sa.Column('salary_match_score', sa.Float(), nullable=True),
        sa.Column('collaborative_score', sa.Float(), nullable=True),
        sa.Column('content_based_score', sa.Float(), nullable=True),
        sa.Column('confidence_level', sa.Float(), nullable=True),
        sa.Column('match_reasons', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('improvement_suggestions', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('calculated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.ForeignKeyConstraint(['candidate_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['job_posting_id'], ['job_postings.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_job_match_scores_candidate_id', 'job_match_scores', ['candidate_id'])
    op.create_index('ix_job_match_scores_job_posting_id', 'job_match_scores', ['job_posting_id'])
    op.create_index('ix_job_match_scores_overall_score', 'job_match_scores', ['overall_score'])
    op.create_index('ix_job_match_scores_calculated_at', 'job_match_scores', ['calculated_at'])
    
    # Create unique constraint for candidate-job pairs
    op.create_index('ix_job_match_scores_unique_pair', 'job_match_scores', ['candidate_id', 'job_posting_id'], unique=True)

    # Create job_recommendations table
    op.create_table('job_recommendations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('candidate_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('job_posting_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('match_score_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('recommendation_type', sa.String(), nullable=False),  # 'automatic', 'skill_update', 'manual'
        sa.Column('recommended_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('viewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('clicked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('applied_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('dismissed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.ForeignKeyConstraint(['candidate_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['job_posting_id'], ['job_postings.id'], ),
        sa.ForeignKeyConstraint(['match_score_id'], ['job_match_scores.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_job_recommendations_candidate_id', 'job_recommendations', ['candidate_id'])
    op.create_index('ix_job_recommendations_job_posting_id', 'job_recommendations', ['job_posting_id'])
    op.create_index('ix_job_recommendations_recommended_at', 'job_recommendations', ['recommended_at'])
    op.create_index('ix_job_recommendations_type', 'job_recommendations', ['recommendation_type'])

    # Create candidate_job_interactions table for collaborative filtering
    op.create_table('candidate_job_interactions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('candidate_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('job_posting_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('interaction_type', sa.String(), nullable=False),  # 'view', 'save', 'apply', 'share'
        sa.Column('interaction_value', sa.Float(), nullable=True),  # Implicit rating (time spent, etc.)
        sa.Column('interaction_metadata', sa.JSON(), nullable=True),  # Additional interaction data
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['candidate_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['job_posting_id'], ['job_postings.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_candidate_job_interactions_candidate_id', 'candidate_job_interactions', ['candidate_id'])
    op.create_index('ix_candidate_job_interactions_job_posting_id', 'candidate_job_interactions', ['job_posting_id'])
    op.create_index('ix_candidate_job_interactions_type', 'candidate_job_interactions', ['interaction_type'])
    op.create_index('ix_candidate_job_interactions_created_at', 'candidate_job_interactions', ['created_at'])

    # Create matching_preferences table
    op.create_table('matching_preferences',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('notification_frequency', sa.String(), default='weekly', nullable=False),  # 'daily', 'weekly', 'monthly', 'never'
        sa.Column('min_match_score', sa.Float(), default=0.6, nullable=False),
        sa.Column('preferred_job_types', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('excluded_companies', postgresql.ARRAY(postgresql.UUID(as_uuid=True)), nullable=True),
        sa.Column('max_commute_distance', sa.Integer(), nullable=True),  # in miles/km
        sa.Column('salary_importance_weight', sa.Float(), default=0.3, nullable=False),
        sa.Column('location_importance_weight', sa.Float(), default=0.2, nullable=False),
        sa.Column('skill_importance_weight', sa.Float(), default=0.5, nullable=False),
        sa.Column('allow_overqualified_matches', sa.Boolean(), default=True, nullable=False),
        sa.Column('allow_underqualified_matches', sa.Boolean(), default=False, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_matching_preferences_user_id', 'matching_preferences', ['user_id'], unique=True)

    # Create job_matching_analytics table
    op.create_table('job_matching_analytics',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('job_posting_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('total_matches_generated', sa.Integer(), default=0, nullable=False),
        sa.Column('high_quality_matches', sa.Integer(), default=0, nullable=False),  # score >= 0.8
        sa.Column('medium_quality_matches', sa.Integer(), default=0, nullable=False),  # 0.6 <= score < 0.8
        sa.Column('low_quality_matches', sa.Integer(), default=0, nullable=False),  # score < 0.6
        sa.Column('total_recommendations_sent', sa.Integer(), default=0, nullable=False),
        sa.Column('total_views_from_recommendations', sa.Integer(), default=0, nullable=False),
        sa.Column('total_applications_from_recommendations', sa.Integer(), default=0, nullable=False),
        sa.Column('average_match_score', sa.Float(), nullable=True),
        sa.Column('recommendation_click_rate', sa.Float(), nullable=True),
        sa.Column('recommendation_application_rate', sa.Float(), nullable=True),
        sa.Column('last_calculated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['job_posting_id'], ['job_postings.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_job_matching_analytics_job_posting_id', 'job_matching_analytics', ['job_posting_id'], unique=True)
    op.create_index('ix_job_matching_analytics_last_calculated_at', 'job_matching_analytics', ['last_calculated_at'])


def downgrade():
    op.drop_table('job_matching_analytics')
    op.drop_table('matching_preferences')
    op.drop_table('candidate_job_interactions')
    op.drop_table('job_recommendations')
    op.drop_table('job_match_scores')