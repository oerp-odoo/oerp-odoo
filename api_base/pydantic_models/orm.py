from extendable_pydantic import ExtendableModelMeta
from pydantic import BaseModel

from odoo.addons.pydantic.utils import GenericOdooGetter

from ..pydantic_models.field import FieldPydantic


class MappedOdooGetter(GenericOdooGetter):
    def get(self, key: any, default: any = None) -> any:
        pm = self._obj.env.context.get('api_base_pydantic_map', {})
        if key in pm:
            field_orm = pm[key]
            # Fetch odoo field.
            val = super().get(field_orm.fname, default=default)
            # Convert to pydantic expected value.
            converter = field_orm.converter
            if converter is not None:
                val = converter(self._obj, val)
            return val
        else:
            return super().get(key, default=default)


class OrmModel(BaseModel, metaclass=ExtendableModelMeta):
    # To do direct mapping between odoo and pydantic models.
    class Config:
        orm_mode = True
        getter_dict = MappedOdooGetter

    @classmethod
    def get_pydantic_map(cls) -> dict[str, FieldPydantic]:
        """Specify mapping to convert data from odoo to pydantic."""
        return {}

    @classmethod
    def from_orm(cls, obj):
        return super().from_orm(
            obj.with_context(api_base_pydantic_map=cls.get_pydantic_map())
        )
