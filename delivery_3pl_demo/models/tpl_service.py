from odoo import models

from odoo.addons.delivery_3pl.value_objects import IntegrationSpec, SaleEvents


def _on_sync_shipment_status(sale):
    if sale.env.context.get('my_integration_1_not_shipped'):
        return None
    return {'carrier_tracking_ref': 'my-ref-123'}


def _is_3pl_line(sale_line):
    # For demo, we want to match all lines unless explicitly stated to
    # be excluded.
    return sale_line.product_id.default_code != 'NOT-3PL'


class TplService(models.Model):
    _inherit = 'tpl.service'

    @property
    def integrations(self):
        res = super().integrations
        res['my_integration_1'] = IntegrationSpec(
            label="My Integration 1",
            sale_events=SaleEvents(
                on_confirm=lambda s: {'tpl_identifier': f'{s.name}-MY-INTEGRATION-ID'},
                on_sync_shipment_status=_on_sync_shipment_status,
            ),
            is_3pl_line=_is_3pl_line,
        )
        return res
