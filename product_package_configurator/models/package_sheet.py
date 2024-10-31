from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from .. import const


class PackageSheet(models.Model):

    _name = 'package.sheet'
    _description = "Package Sheet"

    sheet_type_id = fields.Many2one(
        "package.sheet.type",
        required=True,
        domain="[('scope', '=', scope)]",
    )
    scope = fields.Selection(const.SHEET_TYPE_SELECTION, required=True)
    unit_cost = fields.Float(required=True, digits=const.DecimalPrecision.COST)
    sheet_length = fields.Float(
        "Length, mm", required=True, digits=const.DecimalPrecision.SIZE
    )
    sheet_width = fields.Float(
        "Width, mm", required=True, digits=const.DecimalPrecision.SIZE
    )
    min_qty = fields.Integer(
        string="MOQ",
        help="Minimum order quantity of sheets to be used regardless of how many are"
        + " needed.",
    )
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company', required=True, default=lambda s: s.env.company
    )
    currency_id = fields.Many2one(related='company_id.currency_id')

    @api.depends(
        'sheet_type_id.display_name',
        'sheet_length',
        'sheet_width',
    )
    def _compute_display_name(self):
        for rec in self:
            st = rec.sheet_type_id
            rec.display_name = (
                f"{st.display_name} {rec.sheet_length:2g}x{rec.sheet_width:2g}"
            )

    @api.constrains('scope', 'sheet_type_id')
    def _check_scope(self):
        for rec in self:
            if rec.scope != rec.sheet_type_id.scope:
                raise ValidationError(
                    _(
                        "Sheet (%(scope)s) and its Type (%(type_scope)s) must match"
                        + " same Scope!",
                        scope=rec.scope,
                        type_scope=rec.sheet_type_id.scope,
                    )
                )

    @api.constrains('sheet_length', 'sheet_width')
    def _check_dimensions(self):
        for rec in self:
            if rec.sheet_length <= 0 or rec.sheet_width <= 0:
                raise ValidationError(
                    _("Sheet Length and Width must be greater than 0!")
                )
