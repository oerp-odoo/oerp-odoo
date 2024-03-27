from odoo import models


class StampConfigure(models.TransientModel):
    """Extend to integrate with stock."""

    _inherit = 'stamp.configure'

    def _prepare_mold_product(self):
        res = super()._prepare_mold_product()
        service_to_purchase = self.company_id.service_to_purchase_stamp
        if service_to_purchase:
            res['service_to_purchase'] = service_to_purchase
        return res

    def _prepare_common_product_vals(self, stamp_type):
        # TODO: add support to set `price` on product.supplierinfo
        # record. For this we will need to receive price_unit and cost
        # value in this method.
        res = super()._prepare_common_product_vals(stamp_type)
        partner_supplier = self.company_id.partner_supplier_default_stamp_id
        if partner_supplier:
            cost = getattr(self, f'cost_unit_{stamp_type}')
            res['seller_ids'] = [
                (0, 0, {'partner_id': partner_supplier.id, 'price': cost})
            ]
        return res
