# Re-export all ORM models so that Alembic can discover them via
# ``target_metadata = Base.metadata`` in alembic/env.py
from app.models.user import User  # noqa: F401
from app.models.role import Role  # noqa: F401
from app.models.permission import Permission  # noqa: F401
from app.models.role_permission import RolePermission  # noqa: F401
from app.models.project import Project  # noqa: F401
from app.models.sprint import Sprint  # noqa: F401
from app.models.user_story import UserStory  # noqa: F401
from app.models.task import Task  # noqa: F401
