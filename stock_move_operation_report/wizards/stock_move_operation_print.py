import base64
import csv
from datetime import date, timedelta
from io import StringIO

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

FILENAME = 'product_location_report.csv'
FIELDNAME = 'datas'


class StockPMoveOperationPrint(models.TransientModel):
    _name = 'stock.move.operation.print'
    _description = "Stock Move Operation Print"

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        today = date.today()
        dt_last_month_end = today.replace(day=1) - timedelta(days=1)
        if not res.get('date_start') and 'date_start' in fields_list:
            res['date_start'] = dt_last_month_end.replace(day=1)
        if not res.get('date_end') and 'date_end' in fields_list:
            res['date_end'] = dt_last_month_end
        if not res.get('company_id') and 'company_id' in fields_list:
            res['company_id'] = self.env.company.id
        return res

    date_start = fields.Date(required=True)
    date_end = fields.Date(required=True)
    warehouse_id = fields.Many2one('stock.warehouse')
    company_id = fields.Many2one('res.company', required=True)
    datas = fields.Binary("Data")

    @api.constrains('date_start', 'date_end')
    def _check_dates(self):
        for rec in self:
            if rec.date_start > rec.date_end:
                raise ValidationError(_("Date Start must be sooner than Date End!"))

    def action_print(self):
        self.ensure_one()
        self.datas = self._generate_report_csv_base64_data()
        return {
            'type': 'ir.actions.act_url',
            'url': (
                f'/web/content/{self._name}/{self.id}/'
                + f'{FIELDNAME}/{FILENAME}?download=true'
            ),
        }

    def _generate_report_csv_base64_data(self):
        self.ensure_one()
        data = self.env['stock.move.operation.report'].generate_report_data(
            self.date_start,
            self.date_end,
            self.company_id.id,
            warehouse=self.warehouse_id,
        )
        try:
            # TODO: use custom headers, to make it more user friendly!
            header = data[0].keys()
        except IndexError:
            raise ValidationError("No data found to print!")
        file = StringIO()
        writer = csv.DictWriter(file, header)
        writer.writeheader()
        writer.writerows(data)
        return base64.b64encode(file.getvalue().encode())
