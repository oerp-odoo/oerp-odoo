from odoo import fields, models


class PackageConfigurator(models.AbstractModel):
    _name = 'package.configurator'
    _description = "Package Configurator"

    state = fields.Selection(
        selection=[("draft", "Draft"), ("done", "Done")],
        default="draft",
        required=True,
    )
    base_length = fields.Float(required=True)
    base_width = fields.Float(required=True)
    base_height = fields.Float(required=True)
    company_id = fields.Many2one(
        'res.company', required=True, default=lambda s: s.env.company
    )
    currency_id = fields.Many2one(related='company_id.currency_id')
    circulation_ids = fields.One2many(
        comodel_name='package.configurator.circulation',
        inverse_name='configurator_id',
        string="Circulations",
    )
