from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    service_to_purchase_stamp = fields.Boolean(
        related='company_id.service_to_purchase_stamp',
        readonly=False,
    )
    # TODO: add support for multiple vendors (to set on product) that would
    # be chosen by some rules?
    partner_supplier_default_stamp_id = fields.Many2one(
        related='company_id.partner_supplier_default_stamp_id',
        readonly=False,
    )

    @api.constrains('service_to_purchase_stamp', 'partner_supplier_default_stamp_id')
    def _check_partner_supplier_default_stamp_id(self):
        for rec in self:
            if (
                rec.service_to_purchase_stamp
                and not rec.partner_supplier_default_stamp_id
            ):
                raise ValidationError(
                    _(
                        "To use Service to Purchase for Stamp, you must also"
                        + " select Vendor!"
                    )
                )
