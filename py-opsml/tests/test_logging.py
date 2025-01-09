from opsml.core import LogLevel, OpsmlLogger


def test_loglevel():
    logger = OpsmlLogger.get_logger(LogLevel.Info)

    logger.info("info")
    logger.debug("debug")
    logger.warn("warn")
    logger.error("error")

    logger.info("logging with args: {}", "arg1")
