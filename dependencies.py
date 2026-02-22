# Re-export the get_current_user dependency for use across routers
from app.routers.auth import get_current_user

__all__ = ["get_current_user"]
