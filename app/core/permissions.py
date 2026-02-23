"""Shared permission constants and helpers for the RBAC system."""
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User

ALL_PERMISSIONS: list[str] = [
    "project:read",
    "project:write",
    "sprint:read",
    "sprint:write",
    "story:read",
    "story:write",
    "task:read",
    "task:write",
    "admin:read",
    "admin:write",
    "user:read",
    "user:write",
]


def build_permissions_map(user: "User") -> dict[str, bool]:
    """Return a dict with all 12 permission keys.

    Each value is *True* if the user's role grants that permission,
    *False* otherwise.  Works safely when role_info / role_permissions
    are not loaded (uses empty set).
    """
    granted: set[str] = set()
    role = getattr(user, "role_info", None)
    if role is not None:
        for rp in getattr(role, "role_permissions", []):
            perm = getattr(rp, "permission", None)
            if perm is not None:
                granted.add(perm.name)
    return {perm: (perm in granted) for perm in ALL_PERMISSIONS}
