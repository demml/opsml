from functools import wraps
from typing import Any, Callable

from opsml.helpers.logging import ArtifactLogger

logger = ArtifactLogger.get_logger()


def log_card_change(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator for logging card changes"""

    @wraps(func)
    def wrapper(self, *args, **kwargs) -> None:  # type: ignore[no-untyped-def]
        card, state = func(self, *args, **kwargs)
        repository = str(card.get("repository"))
        name = str(card.get("name"))
        version = str(card.get("version"))
        logger.info(
            "{}: {}/{}/{} {}", self.table_name, repository, name, version, state
        )  # pylint: disable=protected-access

    return wrapper
