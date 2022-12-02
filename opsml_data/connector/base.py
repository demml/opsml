import logging
from typing import Any, Dict, Optional

import requests
from pydantic import BaseModel, Extra
from pyshipt_logging import ShiptLogging
from requests.models import Response


logger = ShiptLogging.get_logger(__name__)


class QueryMetadata(BaseModel):
    query_id: Optional[str] = None
    gcs_url: Optional[str] = None

    class Config:
        extra = Extra.allow


class GCPQueryRunner:
    def __init__(
        self,
        snowflake_api_url: str,
        snowflake_api_auth: str,
    ):
        self.headers = {
            "Accept": "application/json",
            "Authorization": snowflake_api_auth,
        }
        self.gcp_snow_url = snowflake_api_url

        if snowflake_api_auth is None:
            msg = "No authorization or gcp url found. Check your environment variables."  # noqa
            logging.error(msg)
            raise ValueError(msg)

    def _post(self, data: Dict[str, Any]) -> Response:
        response = requests.post(
            f"{self.gcp_snow_url}/v1/query",
            headers=self.headers,
            json=data,
            timeout=3600,
        )

        return response

    def submit_query(
        self,
        query: str,
        to_storage: bool = True,
    ) -> QueryMetadata:
        """
        Submits query and returns query id.

        Args:
            query: SQL query to submit to Snowflake.
        Returns:
            query_id: Snowflake query id.

        """

        data = {
            "query": query,
            "to_storage": to_storage,
        }
        response = self._post(data=data)

        logging.info(response.status_code)
        logging.info(response.json())

        metadata = QueryMetadata(**response.json())

        return metadata
