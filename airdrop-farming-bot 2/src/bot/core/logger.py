import os, logging
from rich.logging import RichHandler
def get_logger(name: str):
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(level)
        rh = RichHandler(rich_tracebacks=True, show_time=False)
        fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s - %(message)s")
        rh.setFormatter(fmt)
        logger.addHandler(rh)
    return logger
