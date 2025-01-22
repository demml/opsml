from opsml.core import RustyLogger, LoggingConfig


def test_loglevel():
    logger = RustyLogger.get_logger(LoggingConfig.default())

    logger.info("info")
    logger.debug("debug")
    logger.warn("warn")
    logger.error("error")

    logger.info("logging with args: {}", "arg1")
