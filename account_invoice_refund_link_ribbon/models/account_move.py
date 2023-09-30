from odoo import models, fields, api


class AccountMove(models.Model):

    _inherit = 'account.move'

    has_refunds = fields.Boolean(compute='_compute_has_refunds')

    @api.depends('refund_invoice_ids')
    def _compute_has_refunds(self):
        for rec in self:
            rec.has_refunds = len(rec.refund_invoice_ids) > 0
