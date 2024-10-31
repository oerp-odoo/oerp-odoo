from odoo import api, fields, models

from .. import const


class PackageSheet(models.AbstractModel):

    _name = 'package.sheet'
    _description = "Package Sheet"

    # name = fields.Char(required=True)
    sheet_type_id = fields.Many2one("package.sheet.type", required=True)
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
