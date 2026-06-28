import logging
import colorlog


def get_logger():
    logger = logging.getLogger("app")

    if logger.hasHandlers():
        return logger  # evita duplicados

    logger.setLevel(logging.DEBUG)

    handler = colorlog.StreamHandler()

    formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s - %(levelname)s - %(message)s",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red",
        },
    )

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger