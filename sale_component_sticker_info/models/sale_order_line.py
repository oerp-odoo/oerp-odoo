from collections import defaultdict

from odoo import api, fields, models

INIT_SEQ = 1
SEP = '-'


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    group_name = fields.Char(readonly=True, copy=False)

    @api.model_create_multi
    def create(self, vals_list):
        recs = super().create(vals_list)
        recs.mapped('order_id.order_line')._set_group_names()
        return recs

    def write(self, vals):
        res = super().write(vals)
        if 'product_id' in vals:
            self.mapped('order_id.order_line')._set_group_names()
        return res

    def unlink(self):
        lines = self.mapped('order_id.order_line')
        res = super().unlink()
        lines.exists()._set_group_names()
        return res

    def _group_lines_by_categ_w_group(self):
        data = defaultdict(lambda: self.browse())
        for line in self:
            group = line.product_id.categ_id.property_group
            if not group:
                continue
            data[group] |= line
        return data

    def _generate_group_name(self, group: str, seq: int):
        self.ensure_one()
        return f'{group}{SEP}{seq}'

    def _set_group_names(self):
        data = self._group_lines_by_categ_w_group()
        group_names = []
        for group, lines in data.items():
            seq = INIT_SEQ
            for line in lines:
                line.group_name = line._generate_group_name(group, seq)
                seq += 1
        return group_names
