from odoo import api, models

from .. import utils
from ..pydantic_models.field import FieldOrm


class PartnerPydanticParser(models.AbstractModel):
    """Parser to map Partner model with res.partner."""

    _name = 'partner.pydantic.parser'
    _inherit = 'pydantic.parser'
    _description = "Partner Pydantic Parser"

    @api.model
    def get_orm_map(self) -> dict[str, FieldOrm]:
        return {
            'partner_type': FieldOrm(
                fname='is_company',
                converter=lambda env, val: True if val == 'company' else False,
            ),
            'address_type': FieldOrm(fname='type'),
            'country_code': FieldOrm(
                fname='country_id', converter=utils.get_country_id
            ),
            'postal': FieldOrm(fname='zip'),
        }
