import re

from odoo import models

from ..const import RE_QTY, STICKER_INFO_SEP


# TODO: utils.py are using similar names, but its used to prepare info on POs and
# here we use info from POs to prepare for CSV export.. We should make names more
# distinguished!
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
        for (sinfo, qty) in self._get_sticker_data(po_line):
            data.append(self._prepare_data_row(po_line, sinfo, qty))
        return data

    def _prepare_data_row(self, po_line, sinfo: str | None, qty: float | None):
        product = po_line.product_id
        if qty is None:
            qty = po_line.product_qty
        return {
            'Internal Reference': product.default_code or None,
            'Vendor Reference': po_line.order_id.partner_ref or None,
            'Name': product.name,
            'Quantity': qty,
            'Info': sinfo,
        }

    def _get_sticker_data(self, po_line):
        sinfos = po_line.component_sticker_info
        if not sinfos:
            # With no sticker infos, we still need to iterate once.
            yield (None, None)
        else:
            for sinfo in sinfos.split(STICKER_INFO_SEP):
                yield self._extract_qty_from_sinfo(sinfo.strip())

    def _get_purchase_line(self, purchases):
        for purchase in purchases:
            for line in purchase.order_line:
                if not line.display_type:
                    yield line

    def _get_sort_key(self):
        # Cast to string to also sort by `None` if no value was set!
        return lambda x: (str(x['Internal Reference']), str(x['Info']))

    def _extract_qty_from_sinfo(self, sinfo: str):
        m = re.match(RE_QTY, sinfo)
        if m:
            # TODO: handle if for some reason expected place of quantity is not
            # a number!
            qty = float(m.groups()[1])
            qty_tag = m.groups()[0]
            sinfo = sinfo.replace(qty_tag, '').strip()
            return (sinfo, qty)
        return (sinfo, None)
