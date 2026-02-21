"""add_task_no_to_tasks

Revision ID: da7353832e1c
Revises: 
Create Date: 2026-02-21 12:46:29.649460

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'da7353832e1c'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'tasks',
        sa.Column('task_no', sa.Integer(), sa.Identity(always=False, start=10000001, cycle=False), nullable=False),
        schema='boards'
    )
    op.create_unique_constraint('uq_tasks_task_no', 'tasks', ['task_no'], schema='boards')


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('uq_tasks_task_no', 'tasks', schema='boards', type_='unique')
    op.drop_column('tasks', 'task_no', schema='boards')
