# sink_handler.py
import logging


class SinkHandler(logging.Handler):
    """A generic handler that calls the provided sink_fn(msg: str) for each record.
    """

    def __init__(self, sink_fn, level=logging.NOTSET):
        super().__init__(level)
        self.sink_fn = sink_fn

    def emit(self, record: logging.LogRecord):
        try:
            msg = self.format(record)
            self.sink_fn(msg)
        except Exception:
            # so you don’t drop logs silently
            self.handleError(record)
