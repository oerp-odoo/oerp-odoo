from odoo import models

from ..utils import STICKER_INFO_SEP


class PurchaseComponentStickerInfo(models.AbstractModel):
    _name = 'purchase.component.sticker.info'
    _description = "Purchase Component Sticker Info"

    def prepare_data(self, purchases):
        data = []
        for po_line in self._get_purchase_line(purchases):
            data.extend(self._prepare_data(po_line))
        return sorted(data, key=self._get_sort_key())

    def _prepare_data(self, po_line):
        data = []
        for gn in self._get_group_names(po_line):
            data.append(self._prepare_data_row(po_line, gn))
        return data

    def _prepare_data_row(self, po_line, group_name):
        product = po_line.product_id
        return {
            'Internal Reference': product.default_code or None,
            'Vendor Reference': po_line.order_id.partner_ref or None,
            'Name': product.name,
            'Quantity': po_line.product_qty,
            'Group Name': group_name,
        }

    def _get_group_names(self, po_line):
        sinfo = po_line.component_sticker_info
        if not sinfo:
            # With no sticker infos, we still need to iterate once.
            return [None]
        return [gn.strip() for gn in sinfo.split(STICKER_INFO_SEP)]

    def _get_purchase_line(self, purchases):
        for purchase in purchases:
            for line in purchase.order_line:
                if not line.display_type:
                    yield line

    def _get_sort_key(self):
        # Cast to string to also sort by `None` if no value was set!
        # return lambda x: (str(x['Internal Reference'], str(x['Group Name'])))
        return lambda x: (str(x['Internal Reference']), str(x['Group Name']))
