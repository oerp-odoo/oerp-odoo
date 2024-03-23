from odoo import models


class StampConfigure(models.TransientModel):
    """Extend to integrate with stock."""

    _inherit = 'stamp.configure'

    def _prepare_mold_product(self, price_unit):
        res = super()._prepare_mold_product(price_unit)
        service_to_purchase = self.company_id.service_to_purchase_stamp
        if service_to_purchase:
            res['service_to_purchase'] = service_to_purchase
        return res

    def _prepare_common_product_vals(self):
        # TODO: add support to set `price` on product.supplierinfo
        # record. For this we will need to receive price_unit and cost
        # value in this method.
        res = super()._prepare_common_product_vals()
        partner_supplier = self.company_id.partner_supplier_default_stamp_id
        if partner_supplier:
            res['seller_ids'] = [(0, 0, {'partner_id': partner_supplier.id})]
        return res
