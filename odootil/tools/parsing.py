from __future__ import annotations

from footil.formatting import strip_space

from odoo.exceptions import ValidationError
from odoo.tools import LazyTranslate

from ..const import DEFAULT_DELIMITER

_lt = LazyTranslate(__name__, default_lang='en_US')


def parse_to_list(
    s: str,
    convert=None,
    delimiter=DEFAULT_DELIMITER,
    validator=None,
    clean_whitespace=False,
):
    if clean_whitespace:
        s = strip_space(s)
    items = s.split(delimiter)
    if convert is not None:
        items = [convert(i) for i in items]
    if validator is not None:
        for i in items:
            validator(i)
    return items


def parse_int_list(s: str, delimiter=DEFAULT_DELIMITER):
    return parse_to_list(s, convert=int, delimiter=delimiter, clean_whitespace=True)


def parse_positive_int_list(s: str, delimiter=DEFAULT_DELIMITER):
    return parse_to_list(
        s,
        convert=int,
        delimiter=delimiter,
        validator=_check_int_is_positive,
        clean_whitespace=True,
    )


def _check_int_is_positive(n: int):
    if n < 0:
        raise ValidationError(_lt("Integers must be 0 or greater!"))
    return True
