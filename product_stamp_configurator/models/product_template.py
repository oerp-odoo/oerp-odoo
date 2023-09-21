from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    stamp_type = fields.Selection(related='categ_id.stamp_type', store=True)
    is_insert_die = fields.Boolean(
        store=True, compute='_compute_is_insert_die', readonly=False
    )

    @api.depends('categ_id.stamp_type')
    def _compute_is_insert_die(self):
        for rec in self:
            if rec.is_insert_die and rec.categ_id.stamp_type != 'die':
                rec.is_insert_die = False
