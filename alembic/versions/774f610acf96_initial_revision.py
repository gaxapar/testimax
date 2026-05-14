"""initial revision

Revision ID: 774f610acf96
Revises: 
Create Date: 2026-05-14 16:28:51.140420

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '774f610acf96'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=False, nullable=False),
        sa.Column('username', sa.String(), nullable=True),
        sa.Column('name', sa.String(), nullable=True),
    )

    op.create_table(
        'mini_tests',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('photo_file_id', sa.String(), nullable=True),
        sa.Column('creator_user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('usages', sa.Integer(), nullable=False, default=0),
    )

    op.create_table(
        'mini_test_answers',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('text', sa.String(), nullable=False),
        sa.Column('photo_file_id', sa.String(), nullable=True),
        sa.Column('mini_test_id', sa.Integer(), sa.ForeignKey('mini_tests.id'), nullable=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    pass
