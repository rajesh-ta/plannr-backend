"""add_permissions_and_role_permissions

Revision ID: c2d3e4f5a6b1
Revises: b1c2d3e4f5a6
Create Date: 2026-02-23 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "c2d3e4f5a6b1"
down_revision: Union[str, Sequence[str], None] = "b1c2d3e4f5a6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # 1. Create boards.permissions table (idempotent)
    # ------------------------------------------------------------------
    op.execute("""
        CREATE TABLE IF NOT EXISTS boards.permissions (
            seq_id  SERIAL,
            id      UUID        NOT NULL DEFAULT gen_random_uuid(),
            name    VARCHAR(100) NOT NULL,
            description TEXT,
            CONSTRAINT permissions_pkey        PRIMARY KEY (id),
            CONSTRAINT permissions_name_key    UNIQUE (name)
        )
    """)

    # ------------------------------------------------------------------
    # 2. Seed the 12 permissions
    # ------------------------------------------------------------------
    op.execute("""
        INSERT INTO boards.permissions (name, description) VALUES
            ('project:read',  'View projects'),
            ('project:write', 'Create, update and delete projects'),
            ('sprint:read',   'View sprints'),
            ('sprint:write',  'Create, update and delete sprints'),
            ('story:read',    'View user stories'),
            ('story:write',   'Create, update and delete user stories'),
            ('task:read',     'View tasks'),
            ('task:write',    'Create, update and delete tasks'),
            ('admin:read',    'View admin panel'),
            ('admin:write',   'Manage users and roles via admin panel'),
            ('user:read',     'View user list'),
            ('user:write',    'Create, update and delete users')
        ON CONFLICT (name) DO NOTHING
    """)

    # ------------------------------------------------------------------
    # 3. Create boards.role_permissions table (idempotent)
    # ------------------------------------------------------------------
    op.execute("""
        CREATE TABLE IF NOT EXISTS boards.role_permissions (
            seq_id        SERIAL,
            id            UUID NOT NULL DEFAULT gen_random_uuid(),
            role_id       UUID NOT NULL,
            permission_id UUID NOT NULL,
            CONSTRAINT role_permissions_pkey PRIMARY KEY (id),
            CONSTRAINT fk_rp_role_id
                FOREIGN KEY (role_id)
                REFERENCES boards.roles (id)
                ON DELETE CASCADE,
            CONSTRAINT fk_rp_permission_id
                FOREIGN KEY (permission_id)
                REFERENCES boards.permissions (id)
                ON DELETE CASCADE,
            CONSTRAINT uq_rp_role_permission
                UNIQUE (role_id, permission_id)
        )
    """)

    # ------------------------------------------------------------------
    # 4. Seed role ↔ permission mappings
    #    Using NOT EXISTS guards for full idempotency.
    # ------------------------------------------------------------------

    # PROJECT_ADMIN — all 12 permissions
    op.execute("""
        INSERT INTO boards.role_permissions (role_id, permission_id)
        SELECT r.id, p.id
        FROM   boards.roles r
               CROSS JOIN boards.permissions p
        WHERE  r.role_name = 'PROJECT_ADMIN'
        ON CONFLICT (role_id, permission_id) DO NOTHING
    """)

    # PROJECT_MANAGER — no admin:read/write, no user:write
    op.execute("""
        INSERT INTO boards.role_permissions (role_id, permission_id)
        SELECT r.id, p.id
        FROM   boards.roles r,
               boards.permissions p
        WHERE  r.role_name = 'PROJECT_MANAGER'
          AND  p.name IN (
                   'project:read', 'project:write',
                   'sprint:read',  'sprint:write',
                   'story:read',   'story:write',
                   'task:read',    'task:write',
                   'user:read'
               )
        ON CONFLICT (role_id, permission_id) DO NOTHING
    """)

    # PROJECT_DEVELOPER — read-only on project/sprint, write on story/task
    op.execute("""
        INSERT INTO boards.role_permissions (role_id, permission_id)
        SELECT r.id, p.id
        FROM   boards.roles r,
               boards.permissions p
        WHERE  r.role_name = 'PROJECT_DEVELOPER'
          AND  p.name IN (
                   'project:read',
                   'sprint:read',
                   'story:read',  'story:write',
                   'task:read',   'task:write'
               )
        ON CONFLICT (role_id, permission_id) DO NOTHING
    """)

    # PROJECT_VIEWER — read-only everywhere
    op.execute("""
        INSERT INTO boards.role_permissions (role_id, permission_id)
        SELECT r.id, p.id
        FROM   boards.roles r,
               boards.permissions p
        WHERE  r.role_name = 'PROJECT_VIEWER'
          AND  p.name IN (
                   'project:read',
                   'sprint:read',
                   'story:read',
                   'task:read'
               )
        ON CONFLICT (role_id, permission_id) DO NOTHING
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS boards.role_permissions")
    op.execute("DROP TABLE IF EXISTS boards.permissions")
