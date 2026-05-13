from odoo import api, fields, models


class ApilogConfigLabel(models.Model):
    _name = 'apilog.config.label'
    _description = "API Log Config Label"

    label_id = fields.Many2one('apilog.label', required=True)
    match_expression = fields.Char(required=True)
    config_id = fields.Many2one('apilog.config', required=True, ondelete='cascade')

    @api.constrains('match_expression')
    def _check_match_expression(self):
        ApilogMatcher = self.env['apilog.matcher']
        for rec in self:
            ApilogMatcher.check_match(rec.match_expression)
