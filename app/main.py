from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.claims import router as claims_router
from app.api.routes.documents import router as documents_router
from app.api.routes.exports import router as exports_router
from app.api.routes.health import router as health_router
from app.api.routes.ingest import router as ingest_router
from app.api.routes.tables import router as tables_router
from app.api.routes.verify import router as verify_router
from app.core.config import ensure_directories, settings


def create_app() -> FastAPI:
    ensure_directories()

    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        version="0.2.0",
        description="ClaimGuard backend",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router)
    app.include_router(ingest_router)
    app.include_router(claims_router)
    app.include_router(verify_router)
    app.include_router(tables_router)
    app.include_router(documents_router)
    app.include_router(exports_router)

    return app


app = create_app()