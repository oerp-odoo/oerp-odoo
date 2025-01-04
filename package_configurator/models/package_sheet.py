from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from .. import const


class PackageSheet(models.Model):

    _name = 'package.sheet'
    _description = "Package Sheet"

    name = fields.Char(compute='_compute_name', store=True)
    sheet_type_id = fields.Many2one(
        "package.sheet.type",
        required=True,
        domain="[('component_kind_ids', 'in', component_kind_ids)]",
    )
    component_kind_ids = fields.Many2many(
        'package.component.kind',
        'package_sheet_component_kind_rel',
        'sheet_id',
        'kind_id',
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

    @api.constrains('component_kind_ids', 'sheet_type_id')
    def _check_component_kind_ids(self):
        for rec in self:
            if not rec.component_kind_ids & rec.sheet_type_id.component_kind_ids:
                raise ValidationError(
                    _(
                        "Sheet (%(kinds1)s) and its Type (%(kinds2)s) must match "
                        + "at least one Component Kind!",
                        kinds1=', '.join(rec.component_kind_ids.mapped('name')),
                        kinds2=', '.join(
                            rec.sheet_type_id.component_kind_ids.mapped('name')
                        ),
                    )
                )

    @api.constrains('sheet_length', 'sheet_width')
    def _check_dimensions(self):
        for rec in self:
            if rec.sheet_length <= 0 or rec.sheet_width <= 0:
                raise ValidationError(
                    _("Sheet Length and Width must be greater than 0!")
                )
