from odoo import api, models

from odoo.addons.apilog.value_objects import RequestDirection


class ApilogConfig(models.Model):
    _inherit = 'apilog.config'

    @api.model
    def get_source_config(self):
        res = super().get_source_config()
        res['http_client'] = {
            'label': "HTTP Client",
            'directions': (RequestDirection.OUTGOING,),
        }
        return res
