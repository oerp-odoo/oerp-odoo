import pydantic
from extendable_pydantic import ExtendableModelMeta

from odoo.exceptions import ValidationError

from odoo.addons.pydantic.utils import GenericOdooGetter

from ..exceptions import UnmappedResponseKeyError
from ..pydantic_models.field import FieldPydantic


class MappedOdooGetter(GenericOdooGetter):
    def get(self, key: any, default: any = None) -> any:
        val = self._get_value(key, default)
        self._validate_none_value(key, val)
        return val

    def _get_value(self, key: any, default: any = None) -> any:
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

    def _validate_none_value(self, key: str, val: any):
        PM = self._obj.env.context['api_base_pydantic_cls']
        if val is None and PM.__fields__[key].required:
            model_name = self._obj._name
            # We raise odoo exception instead of leaving it to raise pydantic one,
            # because it will be treated as 500 error, which would obscure what is
            # happening. Even though technically it is correct as such data is not
            # expected, but it makes debugging much harder!
            raise ValidationError(
                f"Data mismatch. Response for {PM.__name__} can't be generated. "
                + f"Mandatory field '{key}' is not set in backend model {model_name}."
            )
        return True


class OrmModel(pydantic.BaseModel, metaclass=ExtendableModelMeta):
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
        obj = obj.with_context(
            api_base_pydantic_map=cls.get_pydantic_map(), api_base_pydantic_cls=cls
        )
        return super().from_orm(obj)


class OrmModelClean(OrmModel):
    """Class to be used when None values should be excluded from response."""

    class Config:
        exclude_none = True
