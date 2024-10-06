from odoo import api, fields, models

from ..utils import get_sale_mos, prepare_component_sticker_info


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    component_sticker_info = fields.Char(
        readonly=True,
        copy=False,
        help="Will show combined sticker info per single component. "
        + "Info will be separated by ;",
    )

    @api.model
    def _prepare_purchase_order_line_from_procurement(
        self, product_id, product_qty, product_uom, company_id, values, po
    ):
        res = super()._prepare_purchase_order_line_from_procurement(
            product_id, product_qty, product_uom, company_id, values, po
        )
        moves = values.get('move_dest_ids')
        if not moves:
            return res
        # We find MOs for products that are manufactured using
        # this PO line product (component)!
        mos = moves.group_id.mrp_production_ids
        info = prepare_component_sticker_info(get_sale_mos(mos))
        if info:
            res['component_sticker_info'] = info
        return res
