import logging

from odoo import models
from odoo.exceptions import ValidationError
from odoo.fields import Domain

from ..utils.invoice import invoice_3pl_order
from ..utils.picking import auto_finish_picking

_logger = logging.getLogger(__name__)


class TplSaleOrder(models.AbstractModel):
    _name = 'tpl.sale.order'
    _description = "3PL Sale Order"

    def confirm(self, sale):
        on_confirm = sale.tpl_service_id.get_sale_event('on_confirm')
        res = on_confirm(sale)
        sale.write(self._prepare_on_confirm_vals(sale, res))
        carrier = sale.tpl_service_id.carrier_default_id
        if carrier:
            sale.picking_ids.write({'carrier_id': carrier.id})
        return True

    def cancel(self, sale):
        on_cancel = sale.tpl_service_id.get_sale_event('on_cancel')
        # on_cancel event is optional
        res = on_cancel(sale) if on_cancel is not None else {}
        sale.write(self._prepare_on_cancel_vals(sale, res))
        return True

    def draft(self, sale):
        on_draft = sale.tpl_service_id.get_sale_event('on_draft')
        # on_draft event is optional
        res = on_draft(sale) if on_draft is not None else {}
        sale.write(self._prepare_on_draft_vals(sale, res))
        return True

    def sync_shipment_status(self, sale):
        """Check if order already shipped. If yes, update status and finish picking."""
        # Sanity check.
        if sale.tpl_status != 'progress':
            raise ValidationError(
                self.env._(
                    "Can only sync status for In Progress 3PL Sale Order (%s)!",
                    sale.name,
                )
            )
        on_sync_shipment_status = sale.tpl_service_id.get_sale_event(
            'on_sync_shipment_status'
        )
        # Expecting to return dict of values when shipment is done!
        picking_vals = on_sync_shipment_status(sale)
        if picking_vals is None:
            return False
        picking = self._get_picking(sale)
        if picking:
            picking.write(picking_vals)
            auto_finish_picking(picking, raise_exc=False)
        sale_vals = {'tpl_status': 'done'}
        picking_carrier = picking.carrier_id
        if picking_carrier and sale.carrier_id != picking_carrier:
            # Sync carrier.
            sale_vals['carrier_id'] = picking_carrier.id
        sale.write(sale_vals)
        invoice_3pl_order(sale)
        return True

    def cron_sync_shipment_status(self, auto_commit=False, sale_ids=None):
        domain = self._prepare_not_shipped_sales_domain(sale_ids=sale_ids)
        sales = self.env['sale.order'].search(domain)
        for sale in sales:
            try:
                # Passing context to distinguish from manual finish.
                self.with_company(sale.company_id).sync_shipment_status(sale)
                if auto_commit:
                    self.env.cr.commit()  # pylint: disable=E8102
            except Exception:
                msg = (
                    self.env._(
                        "Something went wrong syncing shipment status for sale: %s",
                        sale.name,
                    ),
                )
                if not auto_commit:
                    raise Exception(msg)
                _logger.exception(msg)

    def get_lines(self, sale):
        spec = sale.tpl_service_id.integration_spec
        return sale.order_line.filtered(lambda r: spec.is_3pl_line(r))

    def _prepare_on_confirm_vals(self, sale, extra_vals: dict):
        vals = {
            'tpl_status': 'progress',
        }
        carrier = sale.tpl_service_id.carrier_default_id
        if carrier:
            vals['carrier_id'] = carrier.id
        vals.update(extra_vals)
        return vals

    def _prepare_on_cancel_vals(self, sale, vals: dict):
        return {'tpl_status': 'cancel', **vals}

    def _prepare_on_draft_vals(self, sale, vals: dict):
        return {'tpl_status': False, **vals}

    def _get_picking(self, sale):
        # TODO: handle multiple pickings?
        return sale.picking_ids.filtered(
            lambda r: r.state in ('confirmed', 'assigned')
        )[:1]

    def _prepare_not_shipped_sales_domain(self, sale_ids=None):
        domain = (
            Domain('tpl_status', '=', 'progress')
            & Domain('tpl_identifier', '!=', False)
            & Domain('tpl_service_id.active', '=', True)
        )
        if sale_ids is not None:
            domain &= Domain('id', '=', sale_ids)
        return domain
