from odoo import api, fields, models, tools

from ..const import LaborType
from ..utils.misc import compute_selection_name


class PackageLaborType(models.Model):
    _name = 'package.labor.type'
    _description = "Package Labor Type"

    name = fields.Char(compute='_compute_name', store=True)
    code = fields.Selection(
        selection=[
            (LaborType.GENERIC, "Generic"),
            (LaborType.WRAPPINGPAPER_CLADDING, "Wrapping Paper Cladding"),
            (LaborType.LAMINATION, "Lamination"),
            (LaborType.FOILING, "Foiling"),
            (LaborType.INSERT_PUTTING, "Insert Putting"),
            (LaborType.INSERT_FORMATION, "Insert Formation"),
        ],
        required=True,
    )

    _sql_constraints = [
        (
            'code_uniq',
            'unique (code)',
            'The Code must be unique !',
        )
    ]

    @api.depends('code')
    def _compute_name(self):
        compute_selection_name(self, 'code')

    @api.model
    @tools.ormcache('code')
    def get_id(self, code):
        return self.search([('code', '=', code)]).id

    @api.model_create_multi
    def create(self, vals_list):
        result = super().create(vals_list)
        self.env.registry.clear_cache()
        return result

    def write(self, vals):
        result = super().write(vals)
        self.env.registry.clear_cache()
        return result

    def unlink(self):
        result = super().unlink()
        self.env.registry.clear_cache()
        return result
