from __future__ import annotations

from typing import Callable

from fastapi import Depends, Header, HTTPException, Request, status

from app.auth.rbac import get_permissions_for_role
from app.core.security import decode_access_token
from app.services.user_store import get_user_by_id


AuthenticatedUser = dict



def get_current_user(authorization: str | None = Header(default=None)) -> AuthenticatedUser:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")

    token = authorization.split(" ", 1)[1].strip()
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user_id = payload.get("sub")
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user



def require_permissions(*permissions: str) -> Callable[[AuthenticatedUser], AuthenticatedUser]:
    def dependency(user: AuthenticatedUser = Depends(get_current_user)) -> AuthenticatedUser:
        current_permissions = set(user.get("permissions") or get_permissions_for_role(user.get("role")))
        required = set(permissions)
        if not required.issubset(current_permissions):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return user

    return dependency



def require_roles(*roles: str) -> Callable[[AuthenticatedUser], AuthenticatedUser]:
    allowed = {role.strip().lower() for role in roles}

    def dependency(user: AuthenticatedUser = Depends(get_current_user)) -> AuthenticatedUser:
        if (user.get("role") or "user").strip().lower() not in allowed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Role is not allowed")
        return user

    return dependency



def enforce_same_user_or_permission(
    target_user_id: str,
    user: AuthenticatedUser,
    elevated_permission: str,
) -> None:
    if user.get("id") == target_user_id:
        return

    current_permissions = set(user.get("permissions") or get_permissions_for_role(user.get("role")))
    if elevated_permission in current_permissions:
        return

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")



def enforce_path_user_or_permission(
    request: Request,
    user: AuthenticatedUser,
    elevated_permission: str,
    path_param_name: str = "user_id",
) -> None:
    target_user_id = str(request.path_params.get(path_param_name, "")).strip()
    if not target_user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Target user id is required")
    enforce_same_user_or_permission(target_user_id=target_user_id, user=user, elevated_permission=elevated_permission)
