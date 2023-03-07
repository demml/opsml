from fastapi import APIRouter, Depends

from app.routes import healthcheck


api_router = APIRouter(
    responses={404: {"description": "Not found"}},
)
api_router.include_router(healthcheck.router, tags=["health"], prefix="/opsml")
