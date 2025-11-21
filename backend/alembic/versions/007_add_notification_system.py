"""Add notification system

Revision ID: 007
Revises: 006
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade():
    # Create notification_templates table
    op.create_table('notification_templates',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('category', sa.Enum('JOB_MATCH', 'ASSESSMENT_REMINDER', 'INTERVIEW_SCHEDULED', 'APPLICATION_UPDATE', 'SYSTEM_ALERT', 'SECURITY_ALERT', name='notificationcategory'), nullable=False),
        sa.Column('type', sa.Enum('EMAIL', 'SMS', 'PUSH', 'IN_APP', name='notificationtype'), nullable=False),
        sa.Column('subject_template', sa.String(length=255), nullable=False),
        sa.Column('body_template', sa.Text(), nullable=False),
        sa.Column('variables', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    # Create notifications table
    op.create_table('notifications',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('type', sa.Enum('EMAIL', 'SMS', 'PUSH', 'IN_APP', name='notificationtype'), nullable=False),
        sa.Column('category', sa.Enum('JOB_MATCH', 'ASSESSMENT_REMINDER', 'INTERVIEW_SCHEDULED', 'APPLICATION_UPDATE', 'SYSTEM_ALERT', 'SECURITY_ALERT', name='notificationcategory'), nullable=False),
        sa.Column('priority', sa.Enum('LOW', 'MEDIUM', 'HIGH', 'URGENT', name='notificationpriority'), nullable=True),
        sa.Column('status', sa.Enum('PENDING', 'SENT', 'DELIVERED', 'FAILED', 'READ', name='notificationstatus'), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('data', sa.Text(), nullable=True),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('delivered_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('failed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('failure_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create notification_preferences table
    op.create_table('notification_preferences',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('category', sa.Enum('JOB_MATCH', 'ASSESSMENT_REMINDER', 'INTERVIEW_SCHEDULED', 'APPLICATION_UPDATE', 'SYSTEM_ALERT', 'SECURITY_ALERT', name='notificationcategory'), nullable=False),
        sa.Column('email_enabled', sa.Boolean(), nullable=True),
        sa.Column('sms_enabled', sa.Boolean(), nullable=True),
        sa.Column('push_enabled', sa.Boolean(), nullable=True),
        sa.Column('in_app_enabled', sa.Boolean(), nullable=True),
        sa.Column('immediate', sa.Boolean(), nullable=True),
        sa.Column('daily_digest', sa.Boolean(), nullable=True),
        sa.Column('weekly_digest', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create notification_history table
    op.create_table('notification_history',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('notification_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('attempt_number', sa.String(length=10), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'SENT', 'DELIVERED', 'FAILED', 'READ', name='notificationstatus'), nullable=False),
        sa.Column('response_data', sa.Text(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('attempted_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['notification_id'], ['notifications.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for better performance
    op.create_index('ix_notifications_user_id', 'notifications', ['user_id'])
    op.create_index('ix_notifications_status', 'notifications', ['status'])
    op.create_index('ix_notifications_category', 'notifications', ['category'])
    op.create_index('ix_notifications_created_at', 'notifications', ['created_at'])
    op.create_index('ix_notification_preferences_user_id', 'notification_preferences', ['user_id'])


def downgrade():
    # Drop indexes
    op.drop_index('ix_notification_preferences_user_id', table_name='notification_preferences')
    op.drop_index('ix_notifications_created_at', table_name='notifications')
    op.drop_index('ix_notifications_category', table_name='notifications')
    op.drop_index('ix_notifications_status', table_name='notifications')
    op.drop_index('ix_notifications_user_id', table_name='notifications')
    
    # Drop tables
    op.drop_table('notification_history')
    op.drop_table('notification_preferences')
    op.drop_table('notifications')
    op.drop_table('notification_templates')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS notificationstatus')
    op.execute('DROP TYPE IF EXISTS notificationpriority')
    op.execute('DROP TYPE IF EXISTS notificationcategory')
    op.execute('DROP TYPE IF EXISTS notificationtype')