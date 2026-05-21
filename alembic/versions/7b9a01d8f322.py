"""add referral stats

Revision ID: 7b9a01d8f322
Revises: 774f610acf96
Create Date: 2026-05-20 23:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7b9a01d8f322"
down_revision: Union[str, Sequence[str], None] = "774f610acf96"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "referral_stats",
        sa.Column("slug", sa.String(), primary_key=True, nullable=False),
        sa.Column("new_users_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("old_users_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("referral_stats")
