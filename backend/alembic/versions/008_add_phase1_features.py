"""Add Phase 1 features: Career Coach, Portfolio, Scheduling, Resume Builder

Revision ID: 008
Revises: 007
Create Date: 2025-10-28

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '008'
down_revision = '007'
branch_labels = None
depends_on = None


def upgrade():
    # Career Plans
    op.create_table(
        'career_plans',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('current_role', sa.String(200)),
        sa.Column('target_role', sa.String(200)),
        sa.Column('target_salary', sa.Float()),
        sa.Column('timeline_months', sa.Integer()),
        sa.Column('status', sa.String(50), server_default='active'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_career_plans_user_id', 'career_plans', ['user_id'])

    # Coach Conversations
    op.create_table(
        'coach_conversations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('career_plan_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('messages', postgresql.JSON(astext_type=sa.Text()), server_default='[]'),
        sa.Column('topic', sa.String(200)),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['career_plan_id'], ['career_plans.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_coach_conversations_career_plan_id', 'coach_conversations', ['career_plan_id'])

    # Skill Gaps
    op.create_table(
        'skill_gaps',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('career_plan_id', sa.Integer(), nullable=False),
        sa.Column('skill_name', sa.String(200), nullable=False),
        sa.Column('current_level', sa.Integer()),
        sa.Column('required_level', sa.Integer()),
        sa.Column('priority', sa.String(50)),
        sa.Column('learning_resources', postgresql.JSON(astext_type=sa.Text()), server_default='[]'),
        sa.Column('status', sa.String(50), server_default='identified'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['career_plan_id'], ['career_plans.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Career Milestones
    op.create_table(
        'career_milestones',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('career_plan_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('target_date', sa.DateTime()),
        sa.Column('completed', sa.Boolean(), server_default='false'),
        sa.Column('completed_at', sa.DateTime()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['career_plan_id'], ['career_plans.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Portfolios
    op.create_table(
        'portfolios',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('video_intro_url', sa.String(500)),
        sa.Column('video_duration', sa.Integer()),
        sa.Column('headline', sa.String(200)),
        sa.Column('bio', sa.Text()),
        sa.Column('template_id', sa.String(50), server_default='modern'),
        sa.Column('is_public', sa.Boolean(), server_default='true'),
        sa.Column('view_count', sa.Integer(), server_default='0'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )

    # Portfolio Projects
    op.create_table(
        'portfolio_projects',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('portfolio_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('technologies', postgresql.JSON(astext_type=sa.Text()), server_default='[]'),
        sa.Column('media_urls', postgresql.JSON(astext_type=sa.Text()), server_default='[]'),
        sa.Column('code_snippets', postgresql.JSON(astext_type=sa.Text()), server_default='[]'),
        sa.Column('live_url', sa.String(500)),
        sa.Column('github_url', sa.String(500)),
        sa.Column('display_order', sa.Integer(), server_default='0'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['portfolio_id'], ['portfolios.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Achievements
    op.create_table(
        'achievements',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('portfolio_id', sa.Integer(), nullable=False),
        sa.Column('badge_type', sa.String(100), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('issuer', sa.String(200)),
        sa.Column('date_earned', sa.DateTime()),
        sa.Column('verification_url', sa.String(500)),
        sa.Column('icon', sa.String(100)),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['portfolio_id'], ['portfolios.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Scheduling Preferences
    op.create_table(
        'scheduling_preferences',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('timezone', sa.String(100), server_default='UTC'),
        sa.Column('buffer_minutes', sa.Integer(), server_default='15'),
        sa.Column('working_hours', postgresql.JSON(astext_type=sa.Text()), server_default='{}'),
        sa.Column('calendar_integrations', postgresql.JSON(astext_type=sa.Text()), server_default='[]'),
        sa.Column('auto_accept', sa.Boolean(), server_default='false'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )

    # Scheduled Events
    op.create_table(
        'scheduled_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('interview_id', sa.Integer()),
        sa.Column('organizer_id', sa.Integer(), nullable=False),
        sa.Column('participant_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=False),
        sa.Column('timezone', sa.String(100), server_default='UTC'),
        sa.Column('meeting_url', sa.String(500)),
        sa.Column('status', sa.String(50), server_default='scheduled'),
        sa.Column('reminder_sent', sa.Boolean(), server_default='false'),
        sa.Column('calendar_event_ids', postgresql.JSON(astext_type=sa.Text()), server_default='{}'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['interview_id'], ['interviews.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['organizer_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['participant_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_scheduled_events_start_time', 'scheduled_events', ['start_time'])

    # Availability Slots
    op.create_table(
        'availability_slots',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('event_id', sa.Integer()),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=False),
        sa.Column('is_available', sa.Boolean(), server_default='true'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['event_id'], ['scheduled_events.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Resumes
    op.create_table(
        'resumes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('template_id', sa.String(50), server_default='professional'),
        sa.Column('content', postgresql.JSON(astext_type=sa.Text()), server_default='{}'),
        sa.Column('ats_score', sa.Float()),
        sa.Column('keywords', postgresql.JSON(astext_type=sa.Text()), server_default='[]'),
        sa.Column('is_primary', sa.Boolean(), server_default='false'),
        sa.Column('version', sa.Integer(), server_default='1'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_resumes_user_id', 'resumes', ['user_id'])

    # Resume Exports
    op.create_table(
        'resume_exports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('resume_id', sa.Integer(), nullable=False),
        sa.Column('format', sa.String(50), nullable=False),
        sa.Column('file_url', sa.String(500)),
        sa.Column('file_size', sa.Integer()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['resume_id'], ['resumes.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # ATS Optimizations
    op.create_table(
        'ats_optimizations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('resume_id', sa.Integer(), nullable=False),
        sa.Column('job_id', sa.Integer()),
        sa.Column('score', sa.Float(), nullable=False),
        sa.Column('suggestions', postgresql.JSON(astext_type=sa.Text()), server_default='[]'),
        sa.Column('missing_keywords', postgresql.JSON(astext_type=sa.Text()), server_default='[]'),
        sa.Column('formatting_issues', postgresql.JSON(astext_type=sa.Text()), server_default='[]'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['resume_id'], ['resumes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('ats_optimizations')
    op.drop_table('resume_exports')
    op.drop_index('ix_resumes_user_id', 'resumes')
    op.drop_table('resumes')
    op.drop_table('availability_slots')
    op.drop_index('ix_scheduled_events_start_time', 'scheduled_events')
    op.drop_table('scheduled_events')
    op.drop_table('scheduling_preferences')
    op.drop_table('achievements')
    op.drop_table('portfolio_projects')
    op.drop_table('portfolios')
    op.drop_table('career_milestones')
    op.drop_table('skill_gaps')
    op.drop_index('ix_coach_conversations_career_plan_id', 'coach_conversations')
    op.drop_table('coach_conversations')
    op.drop_index('ix_career_plans_user_id', 'career_plans')
    op.drop_table('career_plans')
