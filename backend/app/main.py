from fastapi import FastAPI

from app.health import router as health_router
from app.observability import install_observability


def create_app() -> FastAPI:
    application = FastAPI(title="Cost Inventory API")
    install_observability(application)
    application.include_router(health_router)
    return application


app = create_app()
