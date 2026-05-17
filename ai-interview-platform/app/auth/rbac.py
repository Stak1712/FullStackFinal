from __future__ import annotations

from typing import Final

ROLE_GUEST: Final[str] = "guest"
ROLE_USER: Final[str] = "user"
ROLE_MANAGER: Final[str] = "manager"
ROLE_ADMIN: Final[str] = "admin"

ALL_ROLES: Final[tuple[str, ...]] = (ROLE_GUEST, ROLE_USER, ROLE_MANAGER, ROLE_ADMIN)

PERMISSION_PLATFORM_READ: Final[str] = "platform:read"
PERMISSION_PROFILE_READ_SELF: Final[str] = "profile:read:self"
PERMISSION_PROFILE_READ_ANY: Final[str] = "profile:read:any"
PERMISSION_USER_LIST_READ: Final[str] = "users:list"
PERMISSION_USER_ROLE_MANAGE: Final[str] = "users:role:manage"
PERMISSION_INTERVIEWS_READ: Final[str] = "interviews:read"
PERMISSION_INTERVIEWS_CREATE: Final[str] = "interviews:create"
PERMISSION_INTERVIEWS_UPDATE: Final[str] = "interviews:update"
PERMISSION_INTERVIEWS_DELETE: Final[str] = "interviews:delete"
PERMISSION_AI_SESSION_CREATE: Final[str] = "ai_sessions:create"
PERMISSION_AI_SESSION_READ_OWN: Final[str] = "ai_sessions:read:own"
PERMISSION_AI_SESSION_READ_ANY: Final[str] = "ai_sessions:read:any"
PERMISSION_AI_SESSION_ANSWER_OWN: Final[str] = "ai_sessions:answer:own"
PERMISSION_AI_SCORE: Final[str] = "ml:score"
PERMISSION_ADMIN_PANEL_ACCESS: Final[str] = "admin:panel"
PERMISSION_RESUMES_UPLOAD: Final[str] = "resumes:upload"
PERMISSION_RESUMES_READ_OWN: Final[str] = "resumes:read:own"
PERMISSION_RESUMES_READ_ANY: Final[str] = "resumes:read:any"
PERMISSION_RESUMES_DOWNLOAD_OWN: Final[str] = "resumes:download:own"
PERMISSION_RESUMES_DOWNLOAD_ANY: Final[str] = "resumes:download:any"

ROLE_PERMISSIONS: Final[dict[str, set[str]]] = {
    ROLE_GUEST: {
        PERMISSION_PLATFORM_READ,
    },
    ROLE_USER: {
        PERMISSION_PLATFORM_READ,
        PERMISSION_PROFILE_READ_SELF,
        PERMISSION_INTERVIEWS_READ,
        PERMISSION_AI_SESSION_CREATE,
        PERMISSION_AI_SESSION_READ_OWN,
        PERMISSION_AI_SESSION_ANSWER_OWN,
        PERMISSION_AI_SCORE,
        PERMISSION_RESUMES_UPLOAD,
        PERMISSION_RESUMES_READ_OWN,
        PERMISSION_RESUMES_DOWNLOAD_OWN,
    },
    ROLE_MANAGER: {
        PERMISSION_PLATFORM_READ,
        PERMISSION_PROFILE_READ_SELF,
        PERMISSION_PROFILE_READ_ANY,
        PERMISSION_USER_LIST_READ,
        PERMISSION_INTERVIEWS_READ,
        PERMISSION_INTERVIEWS_CREATE,
        PERMISSION_INTERVIEWS_UPDATE,
        PERMISSION_AI_SESSION_CREATE,
        PERMISSION_AI_SESSION_READ_OWN,
        PERMISSION_AI_SESSION_READ_ANY,
        PERMISSION_AI_SESSION_ANSWER_OWN,
        PERMISSION_AI_SCORE,
        PERMISSION_RESUMES_UPLOAD,
        PERMISSION_RESUMES_READ_OWN,
        PERMISSION_RESUMES_READ_ANY,
        PERMISSION_RESUMES_DOWNLOAD_OWN,
        PERMISSION_RESUMES_DOWNLOAD_ANY,
    },
    ROLE_ADMIN: {
        PERMISSION_PLATFORM_READ,
        PERMISSION_PROFILE_READ_SELF,
        PERMISSION_PROFILE_READ_ANY,
        PERMISSION_USER_LIST_READ,
        PERMISSION_USER_ROLE_MANAGE,
        PERMISSION_INTERVIEWS_READ,
        PERMISSION_INTERVIEWS_CREATE,
        PERMISSION_INTERVIEWS_UPDATE,
        PERMISSION_INTERVIEWS_DELETE,
        PERMISSION_AI_SESSION_CREATE,
        PERMISSION_AI_SESSION_READ_OWN,
        PERMISSION_AI_SESSION_READ_ANY,
        PERMISSION_AI_SESSION_ANSWER_OWN,
        PERMISSION_AI_SCORE,
        PERMISSION_ADMIN_PANEL_ACCESS,
        PERMISSION_RESUMES_UPLOAD,
        PERMISSION_RESUMES_READ_OWN,
        PERMISSION_RESUMES_READ_ANY,
        PERMISSION_RESUMES_DOWNLOAD_OWN,
        PERMISSION_RESUMES_DOWNLOAD_ANY,
    },
}

ROLE_LABELS: Final[dict[str, str]] = {
    ROLE_GUEST: "Гость",
    ROLE_USER: "Пользователь",
    ROLE_MANAGER: "Менеджер",
    ROLE_ADMIN: "Администратор",
}

ROLE_MATRIX: Final[dict[str, dict[str, object]]] = {
    ROLE_GUEST: {
        "label": ROLE_LABELS[ROLE_GUEST],
        "permissions": sorted(ROLE_PERMISSIONS[ROLE_GUEST]),
        "restrictions": [
            "Доступ только к публичным страницам и информации о платформе.",
            "Закрытые API и пользовательские данные недоступны по умолчанию.",
        ],
    },
    ROLE_USER: {
        "label": ROLE_LABELS[ROLE_USER],
        "permissions": sorted(ROLE_PERMISSIONS[ROLE_USER]),
        "restrictions": [
            "Может работать только со своими данными, своими AI-сессиями и своими резюме.",
            "Не может управлять ролями и удалять служебные записи.",
        ],
    },
    ROLE_MANAGER: {
        "label": ROLE_LABELS[ROLE_MANAGER],
        "permissions": sorted(ROLE_PERMISSIONS[ROLE_MANAGER]),
        "restrictions": [
            "Может модерировать каталог интервью и просматривать загруженные резюме.",
            "Не может менять роли пользователей.",
        ],
    },
    ROLE_ADMIN: {
        "label": ROLE_LABELS[ROLE_ADMIN],
        "permissions": sorted(ROLE_PERMISSIONS[ROLE_ADMIN]),
        "restrictions": [
            "Имеет полный доступ к служебным операциям и управлению ролями.",
            "Используется для административных сценариев и аудита доступа.",
        ],
    },
}


def normalize_role(role: str | None) -> str:
    candidate = (role or ROLE_USER).strip().lower()
    if candidate not in ALL_ROLES:
        raise ValueError(f"Unsupported role: {role}")
    return candidate



def get_permissions_for_role(role: str | None) -> list[str]:
    normalized = normalize_role(role)
    return sorted(ROLE_PERMISSIONS.get(normalized, set()))



def has_permissions(role: str | None, required_permissions: set[str] | list[str] | tuple[str, ...]) -> bool:
    current = set(get_permissions_for_role(role))
    return set(required_permissions).issubset(current)
