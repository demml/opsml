from fastapi import FastAPI, Depends
from opsml_artifacts.helpers.logging import ArtifactLogger


from opsml_artifacts.api.routes.router import api_router
from opsml_artifacts.api.core.event_handlers import start_app_handler, stop_app_handler
from opsml_artifacts.api.core.config import config
from opsml_artifacts.api.core.login import get_current_username


logger = ArtifactLogger.get_logger(__name__)


def get_opsml_app() -> FastAPI:
    fast_app = FastAPI(
        title=config.APP_NAME,
        dependencies=[Depends(get_current_username)],
    )
    fast_app.include_router(api_router)
    fast_app.add_event_handler("startup", start_app_handler())
    fast_app.add_event_handler("shutdown", stop_app_handler())

    return fast_app


app = get_opsml_app()
