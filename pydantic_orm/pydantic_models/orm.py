from __future__ import annotations

from collections.abc import Callable
from typing import Any

import pydantic


class OrmFieldSpec(pydantic.BaseModel):
    """Spec used when converting from odoo to pydantic."""

    model_config = pydantic.ConfigDict(strict=True)

    # TODO: make odoo_field optional, because not all mappings will
    # actually have odoo field!
    odoo_field: str
    # Callable that receives odoo record and value from odoo record
    # that is being converted to pydantic.
    converter: Callable[[Any, Any, Any], Any] | None = None
    submodel: type[OrmModel] | None = None


class OrmModel(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(strict=True)

    @classmethod
    def get_orm_map(cls) -> dict[str, OrmFieldSpec]:
        return {}

    @classmethod
    def get_orm_field_spec(cls, pydantic_field: str, odoo_fields: list) -> OrmFieldSpec:
        orm_map = cls.get_orm_map()
        if pydantic_field in orm_map:
            return orm_map[pydantic_field]
        if pydantic_field in odoo_fields:
            return OrmFieldSpec(odoo_field=pydantic_field)
        raise ValueError(f"No OrmFieldSpec found for {pydantic_field}! ({cls})")
