from functools import wraps

from opsml.helpers.logging import ArtifactLogger

logger = ArtifactLogger.get_logger()


def log_card_change(func):
    """Decorator for logging card changes"""

    @wraps(func)
    def wrapper(self, *args, **kwargs) -> None:
        card, state = func(self, *args, **kwargs)
        name = str(card.get("name"))
        version = str(card.get("version"))
        logger.info("{}: {}, version:{} {}", self.table_name, name, version, state)  # pylint: disable=protected-access

    return wrapper
