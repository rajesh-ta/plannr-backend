"""add_roles_table_and_update_users

Revision ID: b1c2d3e4f5a6
Revises: da7353832e1c
Create Date: 2026-02-22 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'b1c2d3e4f5a6'
down_revision: Union[str, Sequence[str], None] = 'da7353832e1c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # 1. Create boards.roles table
    # ------------------------------------------------------------------
    op.create_table(
        'roles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text('gen_random_uuid()')),
        sa.Column('role_name', sa.String(50), nullable=False, unique=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('TRUE')),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('modified_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        schema='boards',
    )

    # ------------------------------------------------------------------
    # 2. Seed default roles
    # ------------------------------------------------------------------
    op.execute("""
        INSERT INTO boards.roles (role_name, description) VALUES
          ('PROJECT_ADMIN',     'Full access — can manage users, roles, and all project data'),
          ('PROJECT_MANAGER',   'Can manage sprints, stories, and tasks; cannot manage users'),
          ('PROJECT_DEVELOPER', 'Can create and update tasks assigned to them'),
          ('PROJECT_VIEWER',    'Read-only access across the entire project')
        ON CONFLICT (role_name) DO NOTHING;
    """)

    # ------------------------------------------------------------------
    # 3. Extend users table
    # ------------------------------------------------------------------
    op.add_column(
        'users',
        sa.Column('role_id', postgresql.UUID(as_uuid=True), nullable=True),
        schema='boards',
    )
    op.add_column(
        'users',
        sa.Column('status', sa.String(20), nullable=False, server_default='ACTIVE'),
        schema='boards',
    )
    op.add_column(
        'users',
        sa.Column('last_modified_on', sa.TIMESTAMP(), nullable=False,
                  server_default=sa.text('NOW()')),
        schema='boards',
    )
    op.add_column(
        'users',
        sa.Column('last_modified_by', postgresql.UUID(as_uuid=True), nullable=True),
        schema='boards',
    )

    # FK: users.role_id -> roles.id
    op.create_foreign_key(
        'fk_users_role_id', 'users', 'roles',
        ['role_id'], ['id'],
        source_schema='boards', referent_schema='boards',
        ondelete='SET NULL',
    )

    # FK: users.last_modified_by -> users.id
    op.create_foreign_key(
        'fk_users_last_modified_by', 'users', 'users',
        ['last_modified_by'], ['id'],
        source_schema='boards', referent_schema='boards',
        ondelete='SET NULL',
    )

    # ------------------------------------------------------------------
    # 4. Migrate legacy role string -> role_id FK (drop legacy column after)
    # ------------------------------------------------------------------
    op.execute("""
        UPDATE boards.users u
        SET role_id = r.id
        FROM boards.roles r
        WHERE UPPER(u.role) = r.role_name;
    """)
    op.drop_column('users', 'role', schema='boards')


def downgrade() -> None:
    op.add_column('users', sa.Column('role', sa.String(50), nullable=True), schema='boards')
    op.drop_constraint('fk_users_last_modified_by', 'users', schema='boards', type_='foreignkey')
    op.drop_constraint('fk_users_role_id', 'users', schema='boards', type_='foreignkey')
    op.drop_column('users', 'last_modified_by', schema='boards')
    op.drop_column('users', 'last_modified_on', schema='boards')
    op.drop_column('users', 'status', schema='boards')
    op.drop_column('users', 'role_id', schema='boards')
    op.drop_table('roles', schema='boards')
