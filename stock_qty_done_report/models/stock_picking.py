import base64
import csv
import re
from io import StringIO

from odoo import fields, models

FNAME_QTY_DONE_DATAS = 'qty_done_datas'


def get_valid_filename(name):
    s = str(name).strip().replace(" ", "_")
    return re.sub(r"(?u)[^-\w.]", "", s)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    qty_done_datas = fields.Binary(
        "Done Quantity Datas",
        compute='_compute_qty_done_datas',
    )

    def _compute_qty_done_datas(self):
        for picking in self:
            picking.qty_done_datas = picking._generate_qty_done_csv_base64_data()

    def get_qty_done_data(self):
        self.ensure_one()
        data = []
        for line in self.move_line_ids:
            if line.qty_done > 0:
                data.append(line._prepare_qty_done())
        return data

    def action_export_qty_done(self):
        self.ensure_one()
        self._post_message_export_qty_done()
        filename = self._get_export_qty_done_filename()
        return {
            'type': 'ir.actions.act_url',
            'url': (
                f'/web/content/{self._name}/{self.id}/'
                + f'{FNAME_QTY_DONE_DATAS}/{filename}?download=true'
            ),
        }

    def _generate_qty_done_csv_base64_data(self):
        self.ensure_one()
        data = self.get_qty_done_data()
        try:
            header = data[0].keys()
        except IndexError:
            header = {}
        file = StringIO()
        writer = csv.DictWriter(file, header)
        writer.writeheader()
        writer.writerows(data)
        return base64.b64encode(file.getvalue().encode())

    def _get_export_qty_done_filename(self):
        self.ensure_one()
        # Picking name might have invalid chars, so we must clean that
        # up.
        name = get_valid_filename(self.name)
        return f'{name}_qty_done.csv'

    def _post_message_export_qty_done(self):
        self.ensure_one()
        filename = self._get_export_qty_done_filename()
        self.message_post(
            body=f'<p>Exported {filename}</p>',
            message_type='notification',
            subtype_xmlid='mail.mt_note',
        )
