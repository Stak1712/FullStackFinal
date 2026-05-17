from fastapi import APIRouter

from app.api.v1.endpoints import admin, auth, health, interviews, ml, questions, resources, resumes, users
from app.api.v1.endpoints.ai_sessions import router as ai_router


api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(interviews.router, prefix="/interviews", tags=["interviews"])
api_router.include_router(resumes.router, prefix="/resumes", tags=["resumes"])
api_router.include_router(questions.router, prefix="/questions", tags=["questions"])
api_router.include_router(resources.router, prefix="/resources", tags=["resources"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(ml.router, prefix="/ml", tags=["ml"])
api_router.include_router(ai_router, prefix="/ai", tags=["ai"])
