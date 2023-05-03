import uuid
from typing import Any, List, Optional

from fastapi import Body, FastAPI, Header, Request
from fastapi.exceptions import HTTPException

from opsml.deploy.fastapi.pydantic_models import HealthCheck
from opsml.deploy.loader import Model
from opsml.helpers.logging import ArtifactLogger

logger = ArtifactLogger.get_logger(__name__)


async def log_prediction(message: str):
    logger.info(message)


# todo: allow for user-generated background tasks
# maybe use standardized file/form or code structure that user can specify?
class RouteCreator:
    def __init__(self, models: List[Model], route: str, app: FastAPI):
        self.models = models
        self.route = route
        self.app = app

    def _create_model_route(
        self,
        route: str,
        name: str,
        response_sig: Any,
        request_sig: Any,
    ):
        @self.app.post(route, name=name, response_model=response_sig)
        async def predict(
            request: Request,
            payload: request_sig = Body(...),
            x_request_id: Optional[str] = Header(None),
        ) -> response_sig:

            if x_request_id is None:
                x_request_id = str(uuid.uuid4())

            model = getattr(request.app.state, f"{name}")
            prediction = model.predict(payload=payload)

            return response_sig(**prediction)

    def _create_healthcheck(self):
        @self.app.get("/healthcheck", response_model=HealthCheck, name="healthcheck")
        def get_healthcheck() -> HealthCheck:
            return HealthCheck(is_alive=True)

    def _create_healtherror(self):
        @self.app.get("/healtherror", name="healtherror")
        def get_healtherror() -> HealthCheck:
            try:
                var1 = 10
                var2 = 11
                assert var1 == var2
            except Exception:  # pylint: disable=broad-exception-caught
                pass
            raise HTTPException(status_code=500, detail="Test error")

    def _create_route_list(self):
        @self.app.get("/route_list")
        def get_route_list():
            url_list = [{"path": route.path, "name": route.name} for route in self.app.routes]
            return url_list

    def create_model_routes(self):

        for model in self.models:
            self._create_model_route(
                name=f"{model.name}-v{model.version}",
                route=f"{self.route}/{model.name}/v{model.version}",
                request_sig=model.input_sig,
                response_sig=model.output_sig,
            )

        self._create_healthcheck()
        self._create_healtherror()
        self._create_route_list()
        logger.info("Created all routes for model api")
