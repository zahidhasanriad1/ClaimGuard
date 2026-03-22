from fastapi import FastAPI

from app.api.routes.claims import router as claims_router
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
        version="0.1.0",
        description="ClaimGuard backend, Step 8",
    )

    app.include_router(health_router)
    app.include_router(ingest_router)
    app.include_router(claims_router)
    app.include_router(verify_router)
    app.include_router(tables_router)

    return app


app = create_app()