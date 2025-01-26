from odoo import api, fields, models

from .. import const
from ..utils.misc import compute_selection_name


class PackageType(models.Model):
    _name = 'package.type'
    _description = "Package Type"

    name = fields.Char(compute='_compute_name', store=True)
    code = fields.Selection(
        [
            (const.PackageType.BOX, "Box"),
            (const.PackageType.INSERT, "Insert"),
        ],
        required=True,
    )
    component_kind_ids = fields.Many2many(
        'package.component.kind',
        'package_type_component_kind_rel',
        'type_id',
        'kind_id',
        string="Component Kinds",
    )
    component_type_ids = fields.Many2many(
        'package.component.type',
        'package_type_component_type_rel',
        'package_type_id',
        'component_type_id',
        string="Component Types",
        help="Component Types that can be used by this Package Type",
    )

    @api.depends('code')
    def _compute_name(self):
        compute_selection_name(self, 'code')

    _sql_constraints = [
        (
            'code_uniq',
            'unique (code)',
            'The Code must be unique !',
        )
    ]
