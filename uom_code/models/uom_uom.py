from odoo import api, fields, models, tools


class UomUom(models.Model):
    """Extend to add code field."""

    _inherit = 'uom.uom'

    code = fields.Char(index=True, copy=False)

    _sql_constraints = [('code_uniq', 'unique (code)', 'The Code must be unique!')]

    @tools.ormcache('code')
    def get_id(self, code):
        return self.search([('code', '=', code)], limit=1).id

    @api.model_create_multi
    def create(self, vals_list):
        result = super().create(vals_list)
        self.get_id.clear_cache(self)
        return result

    def write(self, vals):
        result = super().write(vals)
        self.get_id.clear_cache(self)
        return result

    def unlink(self):
        result = super().unlink()
        self.get_id.clear_cache(self)
        return result
