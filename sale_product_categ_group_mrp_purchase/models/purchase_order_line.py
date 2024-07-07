from odoo import api, fields, models

from ..utils import gather_group_names_with_sale_orders, prepare_sale_group_name


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    sale_group_name = fields.Char(readonly=True, copy=False)

    @api.model
    def _prepare_purchase_order_line_from_procurement(
        self, product_id, product_qty, product_uom, company_id, values, po
    ):
        res = super()._prepare_purchase_order_line_from_procurement(
            product_id, product_qty, product_uom, company_id, values, po
        )
        moves = values.get('move_dest_ids')
        if moves:
            # We find MOs for products that are manufactured using
            # this PO line product (component)!
            mos = moves.group_id.mrp_production_ids
            products = mos.mapped('product_id')
            data = gather_group_names_with_sale_orders(
                products, mos.move_dest_ids.group_id.sale_id
            )
            if data:
                res['sale_group_name'] = prepare_sale_group_name(data)
        return res
