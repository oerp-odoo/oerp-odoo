from odoo import fields, models


class TplService(models.Model):
    _inherit = 'tpl.service'

    integration = fields.Selection(
        selection_add=[('my_integration_1', 'My Integration 1')],
        ondelete={'my_integration_1': 'cascade'},
    )

    def get_3pl_service_matchers(self):
        res = super().get_3pl_service_matchers()
        res['my_integration_1'] = self._get_my_integration_1_service
        return res

    def _get_my_integration_1_service(self, sale_order):
        return self.search([('integration', '=', 'my_integration_1')], limit=1)
