# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pylint: disable=protected-access

from typing import Any, Dict, List, cast

from fastapi import APIRouter, HTTPException, Request, status

from opsml.app.routes.pydantic_models import GetParameterRequest, Parameters, Success
from opsml.helpers.logging import ArtifactLogger
from opsml.registry.sql.base.server import ServerRunCardRegistry

logger = ArtifactLogger.get_logger()

router = APIRouter()


@router.put("/parameters", name="parameter_put", response_model=Success)
def insert_parameter(request: Request, payload: Parameters) -> Success:
    """Inserts parameters into parameters table

    Args:
        request:
            FastAPI request object
        payload:
            MetricsModel

    Returns:
        200
    """

    run_reg: ServerRunCardRegistry = request.app.state.registries.run._registry

    parameters = cast(List[Dict[str, Any]], payload.model_dump()["parameter"])
    try:
        run_reg.insert_parameter(parameters)
        return Success()
    except Exception as error:
        logger.error(f"Failed to insert parameters: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to insert parameters"
        ) from error


# GET would be used, but we are using POST to allow for a request body so that we can pass in a list of params to retrieve
@router.post("/parameters", response_model=Parameters, name="parameter_get")
def get_parameter(request: Request, payload: GetParameterRequest) -> Parameters:
    """Get parameters from parameters table

    Args:
        request:
            FastAPI request object
        payload:
            GetParameterRequest

    Returns:
        `ParametersModel`
    """

    run_reg: ServerRunCardRegistry = request.app.state.registries.run._registry
    try:
        parameters = run_reg.get_parameter(payload.run_uid, payload.name)
        return Parameters(parameter=parameters)

    except Exception as error:
        logger.error(f"Failed to get parameters: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get parameters"
        ) from error
