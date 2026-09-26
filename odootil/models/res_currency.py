from odoo import api, models, tools
from odoo.exceptions import ValidationError


class ResCurrency(models.Model):
    _inherit = 'res.currency'

    @api.model
    @tools.ormcache('code', 'raise_not_found')
    def get_id(self, code, raise_not_found=False):
        currency = self.search([('name', '=', code)])
        if not currency and raise_not_found:
            raise ValidationError(
                self.env._(
                    "No Currency found with code (currency might be inactive): %s", code
                )
            )
        return currency.id

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
