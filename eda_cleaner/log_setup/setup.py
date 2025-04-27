import logging


# Console handler setup
def setup_console_handler(logger):
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s - %(message)s", datefmt="%H:%M"
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.setLevel(logging.INFO)


# File handler setup
def setup_file_handler(logger, filename="default.log", filemode="a"):
    file_handler = logging.FileHandler(filename=filename, mode=filemode)
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.setLevel(logging.INFO)


# Combined setup (for both console and file)
def setup_file_and_console_handler(
    logger, filename="default.log", filemode="a"
):
    setup_console_handler(logger)
    setup_file_handler(logger, filename, filemode)


# Main logging setup function
def setup(
    logger, mode="c", filename="default.log", filemode="a"
):
    """
    ease of life function, setting up logging
    - default 'c' mode -> info level, console-only
    - 'f' mode writes to a file
    - 'fc' mode writes to both
    - file is at debug level - filename and write mode can be provided
    """
    if mode == "c":  # Console only
        setup_console_handler(logger)
    elif mode == "f":  # File only
        setup_file_handler(logger, filename, filemode)
    elif mode == "fc":  # File and Console
        setup_file_and_console_handler(logger, filename, filemode)
    else:
        raise ValueError(f"Unsupported logging mode: {mode}")
