from typing import Any, Optional

class LogLevel:
    Debug: "LogLevel"
    Info: "LogLevel"
    Warn: "LogLevel"
    Error: "LogLevel"
    Trace: "LogLevel"

class WriteLevel:
    Stdout: "WriteLevel"
    Stderror: "WriteLevel"

class LoggingConfig:
    show_threads: bool
    log_level: LogLevel
    write_level: WriteLevel
    use_json: bool

    def __init__(
        self,
        show_threads: bool = True,
        log_level: LogLevel = LogLevel.Info,
        write_level: WriteLevel = WriteLevel.Stdout,
        use_json: bool = False,
    ) -> None:
        """
        Logging configuration options.

        Args:
            show_threads:
                Whether to include thread information in log messages.
                Default is True.

            log_level:
                Log level for the logger.
                Default is LogLevel.Info.

            write_level:
                Write level for the logger.
                Default is WriteLevel.Stdout.

            use_json:
                Whether to write log messages in JSON format.
                Default is False.
        """

class RustyLogger:
    @staticmethod
    def setup_logging(config: Optional[LoggingConfig] = None) -> None:
        """Setup logging with the provided configuration.

        Args:
            config:
                Logging configuration options.
        """

    @staticmethod
    def get_logger(config: Optional[LoggingConfig] = None) -> "RustyLogger":
        """Get a logger with the provided name.

        Args:
            config:
                Logging configuration options.
        """

    def debug(self, message: str, *args: Any) -> None:
        """Log a debug message.

        Args:
            message:
                Message to log.

            args:
                Additional arguments to format the message.
        """

    def info(self, message: str, *args: Any) -> None:
        """Log an info message.

        Args:
            message:
                Message to log.

            args:
                Additional arguments to format the message.
        """

    def warn(self, message: str, *args: Any) -> None:
        """Log a warning message.

        Args:
            message:
                Message to log.

            args:
                Additional arguments to format the message.
        """

    def error(self, message: str, *args: Any) -> None:
        """Log an error message.

        Args:
            message:
                Message to log.

            args:
                Additional arguments to format the message.
        """

    def trace(self, message: str, *args: Any) -> None:
        """Log a trace message.

        Args:
            message:
                Message to log.

            args:
                Additional arguments to format the message.
        """
