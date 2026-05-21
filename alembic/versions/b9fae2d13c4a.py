"""add op access flags to users

Revision ID: b9fae2d13c4a
Revises: 7b9a01d8f322
Create Date: 2026-05-20 23:48:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b9fae2d13c4a"
down_revision: Union[str, Sequence[str], None] = "7b9a01d8f322"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "users",
        sa.Column("is_op_ref_user", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )
    op.add_column(
        "users",
        sa.Column("op_access_granted", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("users", "op_access_granted")
    op.drop_column("users", "is_op_ref_user")
