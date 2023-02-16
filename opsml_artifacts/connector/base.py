from typing import Any, Dict, Optional, Tuple

import requests
from pydantic import BaseModel, root_validator
from requests.models import Response

from opsml_artifacts.helpers.utils import FindPath
from opsml_artifacts.helpers.logging import ArtifactLogger

logger = ArtifactLogger.get_logger(__name__)


class QueryRunner:
    def __init__(
        self,
        api_prefix: str,
        submit_suffix: str,
        status_suffix: str,
        results_suffix: str,
        headers: Dict[str, Any],
    ):
        self.api_prefix = api_prefix
        self.submit_suffix = submit_suffix
        self.status_suffix = status_suffix
        self.results_suffix = results_suffix
        self.headers = headers

    def load_sql(
        self,
        query: Optional[str] = None,
        sql_file: Optional[str] = None,
    ) -> str:
        sql = query or sql_file

        if sql is None:
            raise ValueError(
                "Either a query or sql file name must be provided",
            )

        if ".sql" in sql:
            sql_path = FindPath.find_filepath(name=sql)
            with open(file=sql_path, mode="r", encoding="utf-8") as file_:
                sql = file_.read()

        return sql

    def submit_query(
        self,
        query: Optional[str] = None,
    ) -> Tuple[Response, str]:

        """Submits a query to run

        Args:
            query (str): Optional query to run
            sql_file (str): Optional sql file to run

        Returns:
            Response
        """

        # logic to get sql file
        response = self._post_request(
            suffix=self.submit_suffix,
            data={"query": query},
        )
        query_id = response.json()["query_id"]

        return response, query_id

    def query_status(self, query_id: str) -> Response:
        """Retrieve status for a given query

        Args:
            query_id (str): Id associated with query

        Returns:
            Response
        """

        return self._post_request(
            suffix=self.status_suffix,
            data={"query_id": query_id},
        )

    def query_results(self, query_id: str):
        """Retrieves results for a given query id

        Args:
            query_id (str): Id associated with query

        Returns:
            Response
        """

        return self._post_request(
            suffix=self.results_suffix,
            data={"query_id": query_id},
        )

    def _post_request(self, suffix, data):

        try:
            response = requests.post(
                f"{self.api_prefix}/{suffix}",
                headers=self.headers,
                json=data,
                timeout=1200,
            )
        except Exception as error:  # pylint: disable=broad-except
            if hasattr(error, "message"):
                logger.error(
                    "Failed request \n Status: %s \n, Message: %s",
                    error.message["response"]["Error"]["Code"],
                    error.message["response"]["Error"]["Message"],
                )
            raise error

        if response.status_code != 200:
            message = str(response.json())
            logger.error(
                "Failed request: %s",
                message,
            )
            raise ValueError(message)

        return response


class GcsFilePath(BaseModel):
    gcs_url: str
    gcs_bucket: str
    gcs_filepath: str
    full_path: Optional[str]

    @root_validator(pre=True)
    def set_extras(cls, values):  # pylint: disable=no-self-argument

        values["full_path"] = f"{values['gcs_bucket']}/{values['gcs_filepath']}"
        return values
