import base64
import csv
import io

from odoo import _, fields, models
from odoo.exceptions import ValidationError

FILENAME_PATTERN = 'component_sticker_info{}.csv'
FIELDNAME = 'data'


class PurchaseComponentStickerInfoExport(models.TransientModel):
    _name = 'purchase.component.sticker.info.export'
    _description = "Purchase Component Sticker Info Export"

    data = fields.Binary()

    def action_export(self):
        self.ensure_one()
        purchases = self.env['purchase.order'].browse(
            self.env.context.get('active_ids')
        )
        self.data = self._generate_csv_base64_data(purchases)
        filename = self._generate_filename(purchases)
        return {
            'type': 'ir.actions.act_url',
            'url': (
                f'/web/content/{self._name}/{self.id}/'
                + f'{FIELDNAME}/{filename}?download=true'
            ),
        }

    def _generate_csv_base64_data(self, purchases):
        self.ensure_one()
        data = self.env['purchase.component.sticker.info'].prepare_data(purchases)
        try:
            header = data[0].keys()
        except IndexError:
            raise ValidationError(_("No data found to export!"))
        file = io.StringIO()
        writer = csv.DictWriter(file, header)
        writer.writeheader()
        writer.writerows(data)
        return base64.b64encode(file.getvalue().encode())

    def _generate_filename(self, purchases):
        if len(purchases) > 1:
            return FILENAME_PATTERN.format('')
        return FILENAME_PATTERN.format(f'_{purchases.name}')
