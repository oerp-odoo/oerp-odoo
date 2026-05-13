from odoo import api, models, tools


class ResCurrency(models.Model):
    _inherit = 'res.currency'

    @api.model
    @tools.ormcache('code')
    def get_id(self, code):
        return self.search([('name', '=', code)]).id

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
