from __future__ import annotations

from typing import Callable, Optional

from extendable_pydantic import ExtendableModelMeta
from pydantic import BaseModel

from odoo import fields


class FieldOrm(BaseModel, metaclass=ExtendableModelMeta):
    """Field used when converting from pedantic to ORM (odoo)."""

    fname: str
    # Used for converting to o2m, m2m data. Expects src_fname to be
    # a sequence.
    x2m: Optional[X2many] = None
    # If existing value is pydantic model itself that should be
    # parsed. subparser value is model name of the subparser.
    subparser: Optional[str] = None
    # Additionally callable that accepts odoo env and src field
    # value to convert and return converted value. If subparser was
    # used, this will get value from subparser.
    converter: Optional[Callable[[any, any], any]] = None


class FieldPydantic(BaseModel, metaclass=ExtendableModelMeta):
    """Field used when converting from odoo to pydantic."""

    # odoo field name
    fname: str
    # Callable that receives odoo record and value from odoo record
    # that is being converted to pydantic.
    converter: Optional[Callable[[any, any], any]] = None


class X2many(BaseModel, metaclass=ExtendableModelMeta):
    cmd: fields.Command
    # If True will iterate over source value to create destination
    # command value. For example if we got list of source values and
    # we want to generate list of destination commands.
    # If False, then whole source value will be used as single value
    # for source command/commands.
    src_iterated: bool = True
