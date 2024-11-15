from odoo import fields, models


class PackagePrintHouse(models.Model):
    _name = 'package.print.house'
    _description = "Package Print House"

    name = fields.Char(required=True)
    print_max_length = fields.Float(
        "Max Printable Length (mm)", help="If zero, means no limit"
    )
    print_max_width = fields.Float(
        "Max Printable Width (mm)", help="If zero, means no limit"
    )
    company_id = fields.Many2one(
        'res.company', required=True, default=lambda s: s.env.company
    )
    print_pricelist_id = fields.Many2one('package.print.pricelist', string="Pricelist")
