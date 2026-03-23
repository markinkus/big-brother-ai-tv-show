from fastapi import APIRouter

from neural_house_api.api.routes.contestants import router as contestants_router
from neural_house_api.api.routes.health import router as health_router
from neural_house_api.api.routes.ws import router as ws_router

health_router_group = APIRouter()
health_router_group.include_router(health_router, tags=["health"])

api_router = APIRouter()
api_router.include_router(contestants_router, prefix="/contestants", tags=["contestants"])
api_router.include_router(ws_router, tags=["events"])
