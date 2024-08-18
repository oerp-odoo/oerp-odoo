from __future__ import annotations

import enum
from typing import Optional

from extendable_pydantic import ExtendableModelMeta
from pydantic import BaseModel, Extra, Field

from ..pydantic_models.field import FieldPydantic
from ..pydantic_models.orm import OrmModel


class PartnerType(str, enum.Enum):
    COMPANY = 'company'
    INDIVIDUAL = 'individual'


class AddressType(str, enum.Enum):
    CONTACT = 'contact'
    INVOICE = 'invoice'
    DELIVERY = 'delivery'
    OTHER = 'other'


class PartnerInput(BaseModel, metaclass=ExtendableModelMeta):
    class Config:
        extra = Extra.forbid

    partner: Partner


class Partner(BaseModel, metaclass=ExtendableModelMeta):
    class Config:
        extra = Extra.forbid

    name: Optional[str] = Field(
        default=None,
        description="Customer or company name. Required if address_type is contact.",
    )
    partner_type: PartnerType
    parent_id: Optional[int] = Field(
        default=None,
        description="Individual parent partner ID. Not usable if partner_type "
        + "is company",
    )
    address_type: Optional[AddressType] = AddressType.CONTACT
    vat: Optional[str] = Field(default=None)
    street: str
    street2: Optional[str] = Field(None, description="Extra street information")
    city: Optional[str] = Field(None)
    country_code: str = Field(..., description="2 letter Country ISO code")
    postal: Optional[str] = Field(None, description="Postal code")
    phone: Optional[str] = None
    mobile: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None


class PartnerResponse(OrmModel, metaclass=ExtendableModelMeta):
    id: int
    name: str
    partner_type: PartnerType
    address_type: AddressType

    @classmethod
    def get_pydantic_map(cls):
        """Override to map not direct fields."""
        return {
            "partner_type": FieldPydantic(
                fname='is_company',
                converter=lambda obj, fname: PartnerType(
                    'company' if obj.is_company else 'individual'
                ),
            ),
            "address_type": FieldPydantic(fname='type'),
        }
