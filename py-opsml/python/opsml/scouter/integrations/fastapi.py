import functools
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Awaitable, Callable, Union

from pydantic import BaseModel

from ..scouter.drift import PsiDriftProfile, SpcDriftProfile  # type: ignore
from ..scouter.queue import ScouterQueue  # type: ignore

try:
    from fastapi import APIRouter, BackgroundTasks, FastAPI, Request
    from fastapi.responses import JSONResponse
except ImportError as exc:
    raise ImportError(
        """FastAPI is not installed as a scouter extra. 
        Install scouter with the fastapi extra (scouter[fastapi]) to use the FastAPI integration."""
    ) from exc


class ScouterMixin:
    def __init__(
        self,
        drift_profile: Union[SpcDriftProfile, PsiDriftProfile],
        config: Any,
    ) -> None:
        self._queue = ScouterQueue(drift_profile, config)

    def add_api_route(self, path: str, endpoint: Callable[..., Awaitable[Any]], **kwargs: Any) -> None:
        if "request" not in endpoint.__code__.co_varnames:
            raise ValueError("Request object must be passed to the endpoint function")

        assert issubclass(
            kwargs["response_model"], BaseModel
        ), "Response model must be specified as a Pydantic BaseModel"

        @functools.wraps(endpoint)
        async def wrapper(request: Request, *args: Any, **kwargs: Any) -> Any:
            # Call the original endpoint function and capture necessary values
            response_data = await endpoint(request, *args, **kwargs)

            response = JSONResponse(content=response_data.model_dump())
            background_tasks = BackgroundTasks()
            background_tasks.add_task(self._queue.insert, request.state.scouter_data)
            response.background = background_tasks

            return response

        super().add_api_route(path, wrapper, **kwargs)  # type: ignore


class ScouterRouter(ScouterMixin, APIRouter):
    def __init__(
        self,
        drift_profile: Union[SpcDriftProfile, PsiDriftProfile],
        config: Any,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        ScouterMixin.__init__(self, drift_profile, config)

        @asynccontextmanager
        async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
            """Lifespan event for scouter monitoring queue.

            Args:
                app:
                    FastAPI application instance.

            Yields:
                None
            """
            yield
            self._queue.flush()

        kwargs["lifespan"] = lifespan
        APIRouter.__init__(self, *args, **kwargs)
