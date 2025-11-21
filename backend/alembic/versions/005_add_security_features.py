"""Add security features including MFA

Revision ID: 005
Revises: 004
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add MFA fields to users table
    op.add_column('users', sa.Column('mfa_enabled', sa.Boolean(), nullable=True, default=False))
    op.add_column('users', sa.Column('mfa_secret', sa.String(), nullable=True))
    op.add_column('users', sa.Column('mfa_backup_codes', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    
    # Add security fields to users table
    op.add_column('users', sa.Column('failed_login_attempts', sa.String(), nullable=True, default='0'))
    op.add_column('users', sa.Column('locked_until', sa.DateTime(timezone=True), nullable=True))
    op.add_column('users', sa.Column('last_login', sa.DateTime(timezone=True), nullable=True))
    
    # Create audit_logs table for security compliance
    op.create_table('audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('action', sa.String(), nullable=False),
        sa.Column('resource', sa.String(), nullable=True),
        sa.Column('resource_id', sa.String(), nullable=True),
        sa.Column('ip_address', sa.String(), nullable=True),
        sa.Column('user_agent', sa.String(), nullable=True),
        sa.Column('details', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('severity', sa.String(), nullable=False, default='INFO'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
    )
    op.create_index(op.f('ix_audit_logs_user_id'), 'audit_logs', ['user_id'], unique=False)
    op.create_index(op.f('ix_audit_logs_action'), 'audit_logs', ['action'], unique=False)
    op.create_index(op.f('ix_audit_logs_timestamp'), 'audit_logs', ['timestamp'], unique=False)
    
    # Create security_events table for threat detection
    op.create_table('security_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('event_type', sa.String(), nullable=False),
        sa.Column('ip_address', sa.String(), nullable=True),
        sa.Column('user_agent', sa.String(), nullable=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('details', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('severity', sa.String(), nullable=False),
        sa.Column('resolved', sa.Boolean(), default=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
    )
    op.create_index(op.f('ix_security_events_event_type'), 'security_events', ['event_type'], unique=False)
    op.create_index(op.f('ix_security_events_ip_address'), 'security_events', ['ip_address'], unique=False)
    op.create_index(op.f('ix_security_events_timestamp'), 'security_events', ['timestamp'], unique=False)
    op.create_index(op.f('ix_security_events_severity'), 'security_events', ['severity'], unique=False)


def downgrade() -> None:
    # Drop security tables
    op.drop_table('security_events')
    op.drop_table('audit_logs')
    
    # Remove security fields from users table
    op.drop_column('users', 'last_login')
    op.drop_column('users', 'locked_until')
    op.drop_column('users', 'failed_login_attempts')
    
    # Remove MFA fields from users table
    op.drop_column('users', 'mfa_backup_codes')
    op.drop_column('users', 'mfa_secret')
    op.drop_column('users', 'mfa_enabled')