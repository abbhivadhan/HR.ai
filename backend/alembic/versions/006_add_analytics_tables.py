"""Add analytics and A/B testing tables

Revision ID: 006
Revises: 005
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade():
    # A/B Tests table
    op.create_table('ab_tests',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('test_name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('creator_id', sa.String(), nullable=False),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('start_date', sa.DateTime(), nullable=True),
        sa.Column('end_date', sa.DateTime(), nullable=True),
        sa.Column('variants', sa.JSON(), nullable=False),
        sa.Column('target_metric', sa.String(100), nullable=False),
        sa.Column('sample_size', sa.Integer(), nullable=False),
        sa.Column('duration_days', sa.Integer(), nullable=True),
        sa.Column('significance_level', sa.Float(), nullable=False, default=0.95),
        sa.Column('current_participants', sa.Integer(), nullable=False, default=0),
        sa.Column('results', sa.JSON(), nullable=True),
        sa.Column('config', sa.JSON(), nullable=True),
        sa.Column('stop_reason', sa.String(100), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # A/B Test Assignments table
    op.create_table('ab_test_assignments',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('test_id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('variant', sa.String(100), nullable=False),
        sa.Column('assigned_at', sa.DateTime(), nullable=False),
        sa.Column('context', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['test_id'], ['ab_tests.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('test_id', 'user_id', name='unique_test_user_assignment')
    )
    
    # A/B Test Conversions table
    op.create_table('ab_test_conversions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('test_id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('variant', sa.String(100), nullable=False),
        sa.Column('metric_value', sa.Float(), nullable=False),
        sa.Column('converted_at', sa.DateTime(), nullable=False),
        sa.Column('event_data', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['test_id'], ['ab_tests.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )
    
    # Analytics Reports table
    op.create_table('analytics_reports',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('report_type', sa.String(100), nullable=False),
        sa.Column('entity_id', sa.String(), nullable=True),
        sa.Column('format', sa.String(20), nullable=False),
        sa.Column('generated_at', sa.DateTime(), nullable=False),
        sa.Column('generated_by', sa.String(), nullable=False),
        sa.Column('time_range', sa.String(50), nullable=True),
        sa.Column('config', sa.JSON(), nullable=True),
        sa.Column('data', sa.JSON(), nullable=True),
        sa.Column('file_path', sa.String(500), nullable=True),
        sa.Column('download_count', sa.Integer(), nullable=False, default=0),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, default='completed'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['generated_by'], ['users.id'], ondelete='CASCADE')
    )
    
    # Scheduled Reports table
    op.create_table('scheduled_reports',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('report_config', sa.JSON(), nullable=False),
        sa.Column('schedule', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.String(), nullable=False),
        sa.Column('next_run', sa.DateTime(), nullable=False),
        sa.Column('last_run', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, default='active'),
        sa.Column('delivery_config', sa.JSON(), nullable=True),
        sa.Column('run_count', sa.Integer(), nullable=False, default=0),
        sa.Column('error_count', sa.Integer(), nullable=False, default=0),
        sa.Column('last_error', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='CASCADE')
    )
    
    # Analytics Alerts table
    op.create_table('analytics_alerts',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('severity', sa.String(20), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('metric', sa.String(100), nullable=False),
        sa.Column('current_value', sa.Float(), nullable=False),
        sa.Column('threshold_value', sa.Float(), nullable=True),
        sa.Column('resolved', sa.Boolean(), nullable=False, default=False),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('resolved_by', sa.String(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['resolved_by'], ['users.id'], ondelete='SET NULL')
    )
    
    # Alert Rules table
    op.create_table('alert_rules',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('metric', sa.String(100), nullable=False),
        sa.Column('condition', sa.String(50), nullable=False),
        sa.Column('threshold', sa.Float(), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=False, default=True),
        sa.Column('notification_channels', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.String(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('last_triggered', sa.DateTime(), nullable=True),
        sa.Column('trigger_count', sa.Integer(), nullable=False, default=0),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='CASCADE')
    )
    
    # Custom Metrics table
    op.create_table('custom_metrics',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('formula', sa.Text(), nullable=False),
        sa.Column('data_sources', sa.JSON(), nullable=False),
        sa.Column('aggregation_method', sa.String(50), nullable=False, default='sum'),
        sa.Column('unit', sa.String(50), nullable=False, default='count'),
        sa.Column('created_by', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('enabled', sa.Boolean(), nullable=False, default=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='CASCADE')
    )
    
    # Custom Metric Values table
    op.create_table('custom_metric_values',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('metric_id', sa.String(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('value', sa.Float(), nullable=False),
        sa.Column('dimensions', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['metric_id'], ['custom_metrics.id'], ondelete='CASCADE')
    )
    
    # Analytics Cache table for performance optimization
    op.create_table('analytics_cache',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('cache_key', sa.String(500), nullable=False),
        sa.Column('data', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('hit_count', sa.Integer(), nullable=False, default=0),
        sa.Column('last_accessed', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('cache_key')
    )
    
    # Create indexes for performance
    op.create_index('idx_ab_tests_status', 'ab_tests', ['status'])
    op.create_index('idx_ab_tests_creator', 'ab_tests', ['creator_id'])
    op.create_index('idx_ab_test_assignments_test_user', 'ab_test_assignments', ['test_id', 'user_id'])
    op.create_index('idx_ab_test_conversions_test', 'ab_test_conversions', ['test_id'])
    op.create_index('idx_analytics_reports_type', 'analytics_reports', ['report_type'])
    op.create_index('idx_analytics_reports_entity', 'analytics_reports', ['entity_id'])
    op.create_index('idx_analytics_reports_generated_by', 'analytics_reports', ['generated_by'])
    op.create_index('idx_scheduled_reports_next_run', 'scheduled_reports', ['next_run'])
    op.create_index('idx_analytics_alerts_timestamp', 'analytics_alerts', ['timestamp'])
    op.create_index('idx_analytics_alerts_resolved', 'analytics_alerts', ['resolved'])
    op.create_index('idx_alert_rules_enabled', 'alert_rules', ['enabled'])
    op.create_index('idx_custom_metric_values_metric_timestamp', 'custom_metric_values', ['metric_id', 'timestamp'])
    op.create_index('idx_analytics_cache_expires', 'analytics_cache', ['expires_at'])
    op.create_index('idx_analytics_cache_key', 'analytics_cache', ['cache_key'])


def downgrade():
    # Drop indexes
    op.drop_index('idx_analytics_cache_key')
    op.drop_index('idx_analytics_cache_expires')
    op.drop_index('idx_custom_metric_values_metric_timestamp')
    op.drop_index('idx_alert_rules_enabled')
    op.drop_index('idx_analytics_alerts_resolved')
    op.drop_index('idx_analytics_alerts_timestamp')
    op.drop_index('idx_scheduled_reports_next_run')
    op.drop_index('idx_analytics_reports_generated_by')
    op.drop_index('idx_analytics_reports_entity')
    op.drop_index('idx_analytics_reports_type')
    op.drop_index('idx_ab_test_conversions_test')
    op.drop_index('idx_ab_test_assignments_test_user')
    op.drop_index('idx_ab_tests_creator')
    op.drop_index('idx_ab_tests_status')
    
    # Drop tables
    op.drop_table('analytics_cache')
    op.drop_table('custom_metric_values')
    op.drop_table('custom_metrics')
    op.drop_table('alert_rules')
    op.drop_table('analytics_alerts')
    op.drop_table('scheduled_reports')
    op.drop_table('analytics_reports')
    op.drop_table('ab_test_conversions')
    op.drop_table('ab_test_assignments')
    op.drop_table('ab_tests')