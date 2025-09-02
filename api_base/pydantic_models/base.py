from extendable_pydantic import ExtendableModelMeta
from pydantic import BaseModel, Extra, root_validator


class BaseModelStrict(BaseModel, metaclass=ExtendableModelMeta):
    """Pydantic base model that restricts to using only specified fields."""

    class Config:
        extra = Extra.forbid


class BaseModelNullable(BaseModel, metaclass=ExtendableModelMeta):
    """Implement nullable fields feature.

    All fields by default are assumed to be not nullable and
    get_nullable_fields can be used to specify which are nullable.
    """

    class Config:
        def schema_extra(schema, model):
            for field_name in model.get_nullable_fields():
                props = schema.get('properties', {})
                field_schema = props.get(field_name)
                if not field_schema:
                    continue
                # If it's a $ref, wrap it to preserve enums
                if '$ref' in field_schema:
                    props[field_name] = {
                        'allOf': [field_schema],
                        'nullable': True,
                    }
                else:
                    field_schema['nullable'] = True

    @classmethod
    def get_nullable_fields(cls) -> list[str]:
        return []

    @root_validator(pre=True)
    def validate_nullable(cls, values):
        for field, value in values.items():
            if value is None and field not in cls.get_nullable_fields():
                raise ValueError(f"Field '{field}' cannot be null")
        return values
