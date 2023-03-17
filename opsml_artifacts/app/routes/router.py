from fastapi import APIRouter

from opsml_artifacts.app.routes import artifacts_routes, healthcheck

api_router = APIRouter(responses={404: {"description": "Not found"}})
api_router.include_router(healthcheck.router, tags=["health"], prefix="/opsml")
api_router.include_router(artifacts_routes.router, tags=["artifacts"], prefix="/opsml")
