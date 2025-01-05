from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from .. import const
from ..utils.search import search_default_component_kind


class PackageSheet(models.Model):

    _name = 'package.sheet'
    _description = "Package Sheet"

    name = fields.Char(compute='_compute_name', store=True)
    sheet_type_id = fields.Many2one(
        "package.sheet.type",
        required=True,
        domain="[('component_kind_id', '=', component_kind_id)]",
    )
    component_kind_id = fields.Many2one(
        'package.component.kind',
        required=True,
        default=search_default_component_kind,
    )
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
    def _compute_name(self):
        for rec in self:
            st = rec.sheet_type_id
            rec.name = f"{st.display_name} {rec.sheet_length:2g}x{rec.sheet_width:2g}"

    @api.constrains('component_kind_id', 'sheet_type_id')
    def _check_component_kind_id(self):
        for rec in self:
            if rec.component_kind_id != rec.sheet_type_id.component_kind_id:
                raise ValidationError(
                    _(
                        "Sheet (%(kind1)s) and its Type (%(kind2)s) must have "
                        + "the same Component Kind!",
                        kind1=rec.component_kind_id.name,
                        kind2=rec.sheet_type_id.component_kind_id.name,
                    )
                )

    @api.constrains('sheet_length', 'sheet_width')
    def _check_dimensions(self):
        for rec in self:
            if rec.sheet_length <= 0 or rec.sheet_width <= 0:
                raise ValidationError(
                    _("Sheet Length and Width must be greater than 0!")
                )
