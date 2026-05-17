from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.api.v1.router import api_router as api_v1_router
from app.api.v1.endpoints.seo import router as seo_router
from app.db.init_db import init_db
from app.services.storage import StorageService

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_v1_router, prefix=settings.API_V1_PREFIX)
app.include_router(seo_router, tags=["seo"])


@app.on_event("startup")
def _startup() -> None:
    init_db()
    StorageService().initialize()


@app.get("/", tags=["root"])
def read_root():
    return {"message": "Welcome to AI Interview Platform API"}
