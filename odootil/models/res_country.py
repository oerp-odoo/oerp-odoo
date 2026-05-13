from odoo import api, models, tools


class ResCountry(models.Model):
    _inherit = 'res.country'

    @api.model
    @tools.ormcache('code')
    def get_id_by_code(self, code):
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
