from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserOut(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: EmailStr
    role: str
    permissions: list[str] = []
    created_at: datetime

    model_config = {"from_attributes": True}


class UserRoleUpdateRequest(BaseModel):
    role: str = Field(min_length=4, max_length=32)


class RBACOverviewResponse(BaseModel):
    roles: dict[str, dict[str, object]]
