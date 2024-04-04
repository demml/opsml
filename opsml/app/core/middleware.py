# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from typing import Any, Awaitable, Callable, Union

import rollbar
from fastapi import Request, Response

from opsml.helpers.logging import ArtifactLogger

logger = ArtifactLogger.get_logger()

MiddlewareReturnType = Union[Awaitable[Any], Response]


async def rollbar_middleware(
    request: Request, call_next: Callable[[Request], MiddlewareReturnType]
) -> MiddlewareReturnType:
    try:
        return await call_next(request)  # type: ignore
    except Exception as ex:  # pylint: disable=broad-except
        rollbar.report_exc_info()
        logger.error("unhandled API error: {}", ex)
        return Response("Internal server error", status_code=500)
