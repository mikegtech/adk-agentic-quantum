# logger.py
import logging
import sys

from .hack_sinks import honeyhive_log, s3_log
from .sink_handler import SinkHandler


def get_logger(name: str, with_console=True, with_s3=False, with_opic=False):
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)
    fmt = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
    formatter = logging.Formatter(fmt)

    if with_console:
        ch = logging.StreamHandler(sys.stdout)
        ch.setFormatter(formatter)
        logger.addHandler(ch)

    if with_s3:
        sh = SinkHandler(s3_log, level=logging.INFO)
        sh.setFormatter(formatter)
        logger.addHandler(sh)

    if with_opic:
        oh = SinkHandler(honeyhive_log, level=logging.WARNING)
        oh.setFormatter(formatter)
        logger.addHandler(oh)

    return logger
