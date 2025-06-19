# utils/log_context.py
import contextvars
import logging

# 1) a ContextVar holding a dict of whatever you want in your logs
current_log_ctx: contextvars.ContextVar[dict] = contextvars.ContextVar("current_log_ctx", default={})

def set_log_context(**kwargs):
    """Merge the passed keys into the current context dict.
    Call this in your before_agent / before_tool hooks.
    """
    ctx = current_log_ctx.get().copy()
    ctx.update(kwargs)
    current_log_ctx.set(ctx)

def clear_log_context():
    """Reset to empty—if you need to wipe between runs."""
    current_log_ctx.set({})

class ContextFilter(logging.Filter):
    """A logging.Filter that pulls in whatever is in current_log_ctx
    and stuffs those values onto each record.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        ctx = current_log_ctx.get()
        for key, value in ctx.items():
            setattr(record, key, value)
        return True
