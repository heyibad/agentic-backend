"""add_performance_indexes

Revision ID: 003
Revises: 002
Create Date: 2025-10-29

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade():
    """Add performance indexes"""
    # Index on conversations.user_id for faster conversation lookups
    op.create_index(
        "idx_conversations_user_id", "conversations", ["user_id"], unique=False
    )

    # Index on messages.conversation_id for faster message history queries
    op.create_index(
        "idx_messages_conversation_id", "messages", ["conversation_id"], unique=False
    )

    # Composite index for conversation lookup by user + id
    op.create_index(
        "idx_conversations_user_id_id", "conversations", ["user_id", "id"], unique=False
    )


def downgrade():
    """Remove performance indexes"""
    op.drop_index("idx_conversations_user_id_id", table_name="conversations")
    op.drop_index("idx_messages_conversation_id", table_name="messages")
    op.drop_index("idx_conversations_user_id", table_name="conversations")
