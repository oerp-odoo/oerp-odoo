from odoo import models, fields, api


class ResUsers(models.Model):
    """Extend to add debug_mode field."""

    _inherit = 'res.users'

    debug_mode = fields.Selection([
            ('debug', 'Developer Mode'),
            ('debug_assets', 'Developer Mode (With Assets)')
        ],
        string="Auto Developer Mode",
        help="Will enable developer mode on login for user"
    )

    @api.model
    def get_debug_parameters(self):
        """Return possible debug parameters."""
        return {
            'debug': '?debug',
            'debug_assets': '?debug=assets'
        }

    def get_debug_parameter(self):
        """Return debug parameter for user if its enabled."""
        self.ensure_one()
        params = self.get_debug_parameters()
        return params.get(self.debug_mode, '')
