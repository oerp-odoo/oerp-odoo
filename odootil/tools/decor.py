"""Module with helper decorators."""

import logging
import warnings
from functools import wraps

from odoo.exceptions import ValidationError

from .record import cleanup_noop_values

_logger = logging.getLogger(__name__)


def deprecated(message=None):
    """Deprecate functions/methods."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            warning = (
                f"{func.__name__} is deprecated and will be removed "
                f"in a future version."
            )
            if message:
                warning += f" {message}"
            warnings.warn(
                warning,
                category=DeprecationWarning,
                stacklevel=2,
            )
            return func(*args, **kwargs)

        return wrapper

    return decorator


def no_noop_write(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        pfx = self._name.replace('.', '_')
        no_noop_key = f'no_noop_write_processed_{pfx}'
        # Don't process no noop if it was already processed.
        if self.env.context.get(no_noop_key):
            return method(self, *args, **kwargs)
        # Assuming that first argument will be vals!
        cleanup_noop_values(self, args[0])
        # TODO: maybe if `vals` becomes empty, we should simply return True
        # instead of calling write at all?
        return method(self.with_context(**{no_noop_key: True}), *args, **kwargs)

    return wrapper


def mute_validation_by_ctx(func):
    """Mute raised ValidationError if enabled.

    Currently, ValidationException might be muted using context variable
    `validation_mute`. Muted exception is logged in server logs and in
    the chatter (in case record has chatter enabled).
    """

    def is_muted(func, context):
        return context.get('validation_mute') or context.get(f'{func.__name__}_mute')

    def exception_log(self, e, no_msg=False):
        msg = "Exception muted: %s"
        # Allow logging message only on those models, which have chatter
        # and there is a single record to post message on (there might
        # be cases when exception occurs on single record over iterated
        # recordset, so there's no logic to log the same message on all
        # records in recordset).
        if len(self) == 1 and not no_msg:
            try:
                self._message_log(body=msg % e.args[0])
            except AttributeError:  # pylint: disable=except-pass
                pass
        _logger.warning(msg, e.args[0])

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except ValidationError as e:
            if is_muted(func, self.env.context):
                exception_log(
                    self, e, no_msg=self.env.context.get('validation_mute_no_msg')
                )
            else:
                raise

    return wrapper
