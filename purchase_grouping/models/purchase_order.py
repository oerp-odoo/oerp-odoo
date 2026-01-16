from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    purchase_grouping_id = fields.Many2one('purchase.grouping', copy=False)
