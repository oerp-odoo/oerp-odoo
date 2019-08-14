import os

from odoo import models, fields, api
from odoo.modules.module import get_module_path

MODULE = 'web_highlight'
PATH_HIGHLIGHT_STYLES = 'static/lib/highlight/styles'
FILE_ENDING = '.css'
DEFAULT_STYLE = 'github.css'
HIGLIGHT_STYLE_PARAM_KEY = 'web_highlight.style'


def _get_highlight_styles_path():
    path_module = get_module_path(MODULE)
    return os.path.join(path_module, PATH_HIGHLIGHT_STYLES)


class ResConfigSettings(models.TransientModel):
    """Extend to add highlight.js styles option."""

    _inherit = 'res.config.settings'

    @api.model
    def _get_highlight_styles(self):
        path_styles = _get_highlight_styles_path()
        # Expect only files inside.
        files = sorted(os.listdir(path_styles))
        return (file for file in files if file.endswith(FILE_ENDING))

    @api.model
    def _get_highlight_style_label(self, style):
        return style.replace(FILE_ENDING, '').replace('-', ' ').title()

    def _get_highlight_style_selection(self):
        get_label = self._get_highlight_style_label
        return [
            (style, get_label(style)) for style in self._get_highlight_styles()
        ]

    highlight_style = fields.Selection(_get_highlight_style_selection)

    @api.model
    def _get_active_highlight_style(self):
        return self.env['ir.config_parameter'].sudo().get_param(
            HIGLIGHT_STYLE_PARAM_KEY, default=DEFAULT_STYLE)

    @api.model
    def get_values(self):
        """Override to get active highlight style."""
        res = super(ResConfigSettings, self).get_values()
        res['highlight_style'] = self._get_active_highlight_style()
        return res

    @api.multi
    def set_values(self):
        """Override to update active highlight style."""
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param(
            HIGLIGHT_STYLE_PARAM_KEY, self.highlight_style)
