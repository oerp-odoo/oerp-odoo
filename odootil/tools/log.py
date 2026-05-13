from functools import singledispatch


@singledispatch
def log_message(exc, logger, **kw):
    """Log message using logger depending on exc type."""
    ...
