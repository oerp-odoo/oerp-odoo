from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    mrp_tracking = fields.Selection(
        [
            ('serial', 'By Unique Serial Number'),
            ('lot', 'By Lots'),
            ('none', 'No Tracking'),
        ],
        string="MRP Tracking",
        required=True,
        default='none',
        compute='_compute_mrp_tracking',
        store=True,
        readonly=False,
        help="Allows to create SN/lots via manufacturing when original"
        + " tracking is not used.",
    )

    @api.depends('type')
    def _compute_mrp_tracking(self):
        self.filtered(
            lambda r: not r.mrp_tracking
            or r.type in ('consu', 'service')
            and r.mrp_tracking != 'none'
        ).mrp_tracking = 'none'

    @api.constrains('tracking', 'mrp_tracking')
    def _check_mrp_tracking(self):
        for rec in self:
            if rec.tracking != 'none' and rec.mrp_tracking != 'none':
                raise ValidationError(
                    _(
                        "MRP Tracking can only be used when standard Tracking is not"
                        + " used!"
                    )
                )
