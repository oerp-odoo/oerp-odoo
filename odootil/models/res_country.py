from odoo import api, models


class ResCountry(models.Model):
    _inherit = 'res.country'

    @api.model
    @api.ormcache('code')
    def get_id_by_code(self, code):
        return self.search([('code', '=', code)]).id

    @api.model_create_multi
    def create(self, vals_list):
        result = super().create(vals_list)
        self.env.transaction.invalidate_ormcache()
        return result

    def write(self, vals):
        result = super().write(vals)
        self.env.transaction.invalidate_ormcache()
        return result

    def unlink(self):
        result = super().unlink()
        self.env.transaction.invalidate_ormcache()
        return result
