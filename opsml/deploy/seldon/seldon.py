from typing import Union, Dict
from opsml.helpers.logging import ArtifactLogger

logger = ArtifactLogger.get_logger(__name__)


class MyModel:
    def __init__(self):
        logger.info("hello")

    def predict_raw(self, request):
        logger.info(request)
        return request


# curl -X POST \
# -H 'Content-Type: application/json' \
# -d '{"data": { "ndarray": [[1,2,3,4]]}}' \
# http://localhost:9000/api/v1.0/predictions
