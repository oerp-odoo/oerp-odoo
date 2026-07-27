from typing import Any, TypeVar

from odoo import models

from ..pydantic_models.orm import OrmFieldSpec, OrmModel

OrmModelT = TypeVar("OrmModelT", bound=OrmModel)


class PydanticOrmDeserializer(models.AbstractModel):
    """Deserialize Odoo record into pydantic model instance."""

    _name = 'pydantic.orm.deserializer'
    _description = "Pydantic ORM Deserializer"

    def deserialize(
        self, record: models.BaseModel, pydantic_model: type[OrmModelT]
    ) -> OrmModelT:
        data = {}
        odoo_fields = list(record._fields.keys())
        for pydantic_field in pydantic_model.model_fields:
            orm_field_spec = pydantic_model.get_orm_field_spec(
                pydantic_field,
                odoo_fields,
            )
            data[pydantic_field] = self._convert_odoo_value(
                record, pydantic_model, orm_field_spec
            )
        return pydantic_model(**data)

    def _convert_odoo_value(
        self,
        record: models.BaseModel,
        pydantic_model: type[OrmModelT],
        orm_field_spec: OrmFieldSpec,
    ) -> Any:
        odoo_field = record._fields[orm_field_spec.odoo_field]
        value = record[orm_field_spec.odoo_field]
        if odoo_field.type in ('many2one', 'many2many', 'one2many'):
            if not value:
                return None
            if not orm_field_spec.submodel:
                raise ValueError("OrmFieldSpec must have submodel for relation fields!")
            if odoo_field.type == 'many2one':
                return self._convert_m2o_value(record, orm_field_spec)
            return self._convert_x2m_value(record, orm_field_spec)
        if orm_field_spec.converter is not None:
            return orm_field_spec.converter(
                record,
                record[orm_field_spec.odoo_field],
                pydantic_model,
            )
        if value is False and odoo_field.type != 'boolean':
            return None
        if odoo_field.type in ('date', 'datetime') and not value:
            return None
        return value

    def _convert_m2o_value(
        self, record: models.BaseModel, orm_field_spec: OrmFieldSpec
    ) -> OrmModel:
        # TODO: redundant, but doing it just to make it friendly with typing.
        assert orm_field_spec.submodel is not None
        rel_record = record[orm_field_spec.odoo_field]
        return self.deserialize(rel_record, orm_field_spec.submodel)

    def _convert_x2m_value(
        self, record: models.BaseModel, orm_field_spec: OrmFieldSpec
    ) -> list[OrmModel]:
        res = []
        # TODO: redundant, but doing it just to make it friendly with typing.
        assert orm_field_spec.submodel is not None
        for rel_record in record[orm_field_spec.odoo_field]:
            res.append(self.deserialize(rel_record, orm_field_spec.submodel))
        return res
