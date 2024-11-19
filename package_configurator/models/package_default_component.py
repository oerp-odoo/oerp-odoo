from odoo import api, fields, models

from .. import utils


class PackageDefaultComponent(models.Model):
    _name = 'package.default.component'
    _description = "Package Default Component"

    component_type = fields.Selection(
        lambda s: s.env[
            'package.configurator.box.component'
        ]._get_component_type_selection(),
        required=True,
        default='base_greyboard',
    )
    company_id = fields.Many2one(
        'res.company', required=True, default=lambda s: s.env.company
    )

    _sql_constraints = [
        (
            'component_type_company_id_uniq',
            'unique (component_type, company_id)',
            'The Component Type must be unique per company!',
        )
    ]

    @api.depends('component_type')
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = utils.misc.get_selection_label(rec, 'component_type')
