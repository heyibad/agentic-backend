"""Add OAuth fields to users table

Revision ID: 002
Revises: 001
Create Date: 2025-10-14

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add OAuth-related columns to users table"""
    # Add OAuth provider column
    op.add_column("users", sa.Column("oauth_provider", sa.Text(), nullable=True))

    # Add OAuth ID column with index
    op.add_column("users", sa.Column("oauth_id", sa.Text(), nullable=True))
    op.create_index("ix_users_oauth_id", "users", ["oauth_id"], unique=False)

    # Add is_oauth_user flag
    op.add_column(
        "users",
        sa.Column(
            "is_oauth_user", sa.Boolean(), nullable=False, server_default="false"
        ),
    )


def downgrade() -> None:
    """Remove OAuth-related columns from users table"""
    op.drop_index("ix_users_oauth_id", table_name="users")
    op.drop_column("users", "is_oauth_user")
    op.drop_column("users", "oauth_id")
    op.drop_column("users", "oauth_provider")
