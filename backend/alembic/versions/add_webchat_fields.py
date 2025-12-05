"""
Database migration: Add web chat fields to ChatSession model

Revision ID: add_webchat_fields
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'add_webchat_fields'
down_revision = None  # Update this with the previous migration ID
branch_labels = None
depends_on = None


def upgrade():
    """Add web chat specific fields to chat_sessions table"""
    
    # Add new columns
    op.add_column('chat_sessions', sa.Column('is_web_chat', sa.Boolean(), server_default='false', nullable=False))
    op.add_column('chat_sessions', sa.Column('websocket_session_id', sa.String(), nullable=True))
    op.add_column('chat_sessions', sa.Column('last_activity', sa.DateTime(), server_default=sa.text('now()'), nullable=False))
    op.add_column('chat_sessions', sa.Column('language_used', sa.String(), nullable=True))


def downgrade():
    """Remove web chat specific fields from chat_sessions table"""
    
    op.drop_column('chat_sessions', 'language_used')
    op.drop_column('chat_sessions', 'last_activity')
    op.drop_column('chat_sessions', 'websocket_session_id')
    op.drop_column('chat_sessions', 'is_web_chat')
