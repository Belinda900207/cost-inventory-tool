from fastapi import FastAPI

from app.auth.router import router as auth_router
from app.health import router as health_router
from app.inventory.router import router as inventory_router
from app.observability import install_observability
from app.simulations.router import router as simulations_router


def create_app() -> FastAPI:
    application = FastAPI(title="Cost Inventory API")
    install_observability(application)
    application.include_router(health_router)
    application.include_router(auth_router)
    application.include_router(inventory_router)
    application.include_router(simulations_router)
    return application


app = create_app()
