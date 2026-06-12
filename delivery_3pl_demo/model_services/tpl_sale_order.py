from odoo import models


class TplSaleOrder(models.AbstractModel):
    _inherit = 'tpl.sale.order'

    def _on_confirm_my_integration_1(self, sale):
        return {'tpl_identifier': f'{sale.name}-MY-INTEGRATION-ID'}

    def _sync_shipment_status_my_integration_1(self, sale):
        if sale.env.context.get('my_integration_1_not_shipped'):
            return None
        return {'carrier_tracking_ref': 'my-ref-123'}
