"""
setup.py

Provides flexible logging setup for console and file output.

Public Functions:
- setup(logger, mode='c', filename='default.log', filemode='a'): Sets up logging based on a simple mode string.

Private Functions:
- setup_console_handler(logger): Adds a console handler with INFO level.
- setup_file_handler(logger, filename, filemode): Adds a file handler with DEBUG level.
- setup_file_and_console_handler(logger, filename, filemode): Adds both handlers.
"""

import logging


def setup_console_handler(logger: logging.Logger) -> None:
    """Adds a console handler to the logger with INFO level.

    Args:
        logger (logging.Logger): The logger to configure.
    """
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s - %(message)s", datefmt="%H:%M"
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)


def setup_file_handler(
    logger: logging.Logger, filename="default.log", filemode="a"
) -> None:
    """Adds a file handler to the logger with DEBUG level.

    Args:
        logger (logging.Logger): The logger to configure.
        filename (str, optional): Path to log file. Defaults to 'default.log'.
        filemode (str, optional): File mode ('a' for append, 'w' for overwrite). Defaults to 'a'.
    """
    file_handler = logging.FileHandler(filename=filename, mode=filemode)
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


def setup_file_and_console_handler(
    logger: logging.Logger,
    filename: str = "default.log",
    filemode: str = "a",
) -> None:
    """Adds both console and file handlers to the logger.

    Args:
        logger (logging.Logger): The logger to configure.
        filename (str, optional): Log file path. Defaults to 'default.log'.
        filemode (str, optional): File mode. Defaults to 'a'.
    """
    setup_console_handler(logger)
    setup_file_handler(logger, filename, filemode)


def setup(
    logger: logging.Logger,
    mode: str = "c",
    filename: str = "default.log",
    filemode="a",
) -> None:
    """Convenience function to set up logging for console, file, or both.

    Args:
        logger (logging.Logger): The logger to configure.
        mode (str, optional): One of:
            - 'c': Console only (default, INFO level)
            - 'f': File only (DEBUG level)
            - 'fc': File and Console
        filename (str, optional): File path if using file logging. Defaults to 'default.log'.
        filemode (str, optional): Mode for file handler ('a' for append, 'w' for write). Defaults to 'a'.

    Raises:
        ValueError: If mode is not one of ['c', 'f', 'fc'].
    """
    if mode == "c":  # Console only
        setup_console_handler(logger)
    elif mode == "f":  # File only
        setup_file_handler(logger, filename, filemode)
    elif mode == "fc":  # File and Console
        setup_file_and_console_handler(logger, filename, filemode)
    else:
        raise ValueError(f"Unsupported logging mode: {mode}")

    logger.setLevel(logging.DEBUG)
