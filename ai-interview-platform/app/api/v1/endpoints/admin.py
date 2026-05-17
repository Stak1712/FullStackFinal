from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.dependencies import require_permissions
from app.auth.rbac import PERMISSION_ADMIN_PANEL_ACCESS, PERMISSION_USER_ROLE_MANAGE, ROLE_MATRIX
from app.schemas.user import RBACOverviewResponse, UserOut, UserRoleUpdateRequest
from app.services.user_store import list_users, update_user_role


router = APIRouter()


@router.get("/rbac", response_model=RBACOverviewResponse)
async def get_rbac_overview(_user=Depends(require_permissions(PERMISSION_ADMIN_PANEL_ACCESS))):
    return RBACOverviewResponse(roles=ROLE_MATRIX)


@router.get("/users", response_model=list[UserOut])
async def admin_list_users(_user=Depends(require_permissions(PERMISSION_ADMIN_PANEL_ACCESS))):
    return [UserOut.model_validate(row) for row in list_users()]


@router.patch("/users/{user_id}/role", response_model=UserOut)
async def change_user_role(
    user_id: str,
    payload: UserRoleUpdateRequest,
    _user=Depends(require_permissions(PERMISSION_USER_ROLE_MANAGE)),
):
    try:
        updated = update_user_role(user_id=user_id, new_role=payload.role)
        return UserOut.model_validate(updated)
    except ValueError as exc:
        detail = str(exc)
        if detail == "User not found":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
