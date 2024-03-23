from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    service_to_purchase_stamp = fields.Boolean()
    partner_supplier_default_stamp_id = fields.Many2one('res.partner')
