from extendable_pydantic import ExtendableModelMeta
from pydantic import BaseModel, Extra


class BaseModelStrict(BaseModel, metaclass=ExtendableModelMeta):
    """Pydantic base model that restricts to using only specified fields."""

    class Config:
        extra = Extra.forbid
