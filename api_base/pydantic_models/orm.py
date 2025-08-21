from extendable_pydantic import ExtendableModelMeta
from pydantic import BaseModel

from odoo.addons.pydantic.utils import GenericOdooGetter

from ..exceptions import UnmappedResponseKeyError
from ..pydantic_models.field import FieldPydantic


class MappedOdooGetter(GenericOdooGetter):
    def get(self, key: any, default: any = None) -> any:
        pm = self._obj.env.context.get('api_base_pydantic_map', {})
        if key in pm:
            field_orm = pm[key]
            # Fetch odoo field.
            if field_orm.fname is not None:
                return super().get(field_orm.fname, default=default)
            return field_orm.converter(self._obj)
        elif key not in self._obj._fields:
            raise UnmappedResponseKeyError(
                f"{key} key is not mapped with any of {self._obj._name} fields"
            )
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
        obj = obj.with_context(api_base_pydantic_map=cls.get_pydantic_map())
        return super().from_orm(obj)


class OrmModelClean(OrmModel):
    """Class to be used when None values should be excluded from response."""

    class Config:
        exclude_none = True
