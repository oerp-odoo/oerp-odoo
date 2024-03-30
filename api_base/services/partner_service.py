from odoo.exceptions import ValidationError

from odoo.addons.base_rest import restapi
from odoo.addons.component.core import Component

from ..pydantic_models import partner as pm_partner


class PartnerService(Component):
    """Service to create/update partners."""

    _inherit = 'base.rest.service'
    _name = 'partner.service'
    _usage = 'partners'
    _collection = 'base.services'
    _description = """Service to create/update partners."""

    @restapi.method(
        [(["/"], "POST")],
        input_param=restapi.PydanticModel(pm_partner.PartnerInput),
        output_param=restapi.PydanticModel(pm_partner.PartnerResponse),
    )
    def create(self, partner_in: pm_partner.PartnerInput):
        """Create partner using input data."""
        self._validate_partner_input(partner_in)
        partner = self.env['res.partner'].create(self._prepare_partner(partner_in))
        self._postprocess_create(partner_in, partner)
        return pm_partner.PartnerResponse.from_orm(partner)

    def _validate_partner_input(self, partner_in: pm_partner.PartnerInput):
        partner = partner_in.partner
        # Doing same validation as in standard, but to avoid postgres
        # error, so we can raise ours.
        if not partner.name and partner.address_type == 'contact':
            raise ValidationError(
                "Name is required for Partner with AddressType as CONTACT"
            )
        return True

    def _prepare_partner(self, partner_in: pm_partner.PartnerInput):
        return self.env['partner.pydantic.parser'].parse(partner_in.partner)

    def _postprocess_create(self, partner_in: pm_partner.PartnerInput, partner):
        ...
