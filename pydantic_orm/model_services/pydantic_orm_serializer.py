from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from odoo import models

from ..pydantic_models.orm import OrmFieldSpec, OrmModel


class PydanticOrmSerializer(models.AbstractModel):
    """Deserialize Odoo record into pydantic model instance."""

    _name = 'pydantic.orm.serializer'
    _description = "Pydantic ORM Serializer"

    def serialize(
        # odoo_model can also be a record!
        self,
        obj: OrmModel,
        odoo_model: models.BaseModel,
    ) -> dict:
        data = {}
        obj_type = type(obj)
        odoo_fields = list(odoo_model._fields.keys())
        for pydantic_field in obj_type.model_fields:
            orm_field_spec = obj_type.get_orm_field_spec(pydantic_field, odoo_fields)
            value = self._convert_pydantic_value(
                obj,
                pydantic_field,
                odoo_model,
                orm_field_spec,
            )
            if value is None:
                continue
            data[orm_field_spec.odoo_field] = value
        return data

    def _convert_pydantic_value(
        self,
        obj: OrmModel,
        pydantic_field: str,
        odoo_model: models.BaseModel,
        orm_field_spec: OrmFieldSpec,
    ) -> Any:
        odoo_field = odoo_model._fields[orm_field_spec.odoo_field]
        value = getattr(obj, pydantic_field)
        if odoo_field.type in ('many2one', 'many2many', 'one2many'):
            if value is None:
                return None
            if odoo_field.type == 'many2one':
                return self._convert_to_m2o(value, odoo_model, orm_field_spec)
            return self._convert_to_x2m(value, odoo_model, orm_field_spec)
        if orm_field_spec.converter is not None:
            return orm_field_spec.converter(obj, value, odoo_model)
        return value

    def _convert_to_m2o(
        self,
        value: OrmModel,
        odoo_model: models.BaseModel,
        orm_field_spec: OrmFieldSpec,
    ) -> dict:
        if orm_field_spec.converter is not None:
            # We don't have converted value here, because `value` is already converted
            # in related model one.
            return orm_field_spec.converter(value, None, odoo_model)
        rel_model = odoo_model[orm_field_spec.odoo_field]
        return self.serialize(value, rel_model)

    def _convert_to_x2m(
        self,
        value: list[OrmModel] | OrmModel,
        odoo_model: models.BaseModel,
        orm_field_spec: OrmFieldSpec,
    ) -> list[OrmModel]:
        res = []
        values = value if isinstance(value, Sequence) else [value]
        rel_model = odoo_model[orm_field_spec.odoo_field]
        for v in values:
            serialized_value = self.serialize(v, rel_model)
            if orm_field_spec.converter is not None:
                v = orm_field_spec.converter(v, serialized_value, rel_model)
            res.append(v)
        return res
