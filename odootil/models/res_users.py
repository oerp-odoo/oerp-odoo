from odoo import _, api, models, tools
from odoo.exceptions import ValidationError


class ResUsers(models.Model):
    _inherit = 'res.users'

    @tools.ormcache('self.env.uid', 'login', 'ci')
    def get_id(self, login, ci=False):
        login_search = login.lower() if ci else login
        user = self.env['res.users'].search([('login', '=', login_search)], limit=1)
        if not user:
            raise ValidationError(
                _("No user found with %s. It might be deactivated.", login)
            )
        return user.id

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        self.env.registry.clear_cache()
        return records

    def write(self, vals):
        result = super().write(vals)
        if 'active' in vals or 'login' in vals:
            self.env.registry.clear_cache()
        return result

    def unlink(self):
        result = super().unlink()
        self.env.registry.clear_cache()
        return result
