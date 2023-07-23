from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    property_stamp_pricelist_id = fields.Many2one(
        'stamp.pricelist',
        company_dependent=True,
        string="Stamp Pricelist",
    )

    def _commercial_fields(self):
        return super()._commercial_fields() + ['property_stamp_pricelist_id']
