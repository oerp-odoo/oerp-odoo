import base64
import csv
from datetime import date, timedelta
from io import StringIO

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

FILENAME_PATTERN = 'sold_qty_report_{}_{}.csv'
FIELDNAME = 'datas'
DT_FMT = '%Y%m%d'


class AccountSoldQtyReportPrint(models.TransientModel):
    _name = 'account.sold.qty.report.print'
    _description = "Account Sold Quantities Report Print"

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
        if res.get('company_id'):
            country_id = self.env['res.company'].browse(res['company_id']).country_id.id
            res['country_ids'] = [(4, country_id)]
        return res

    date_start = fields.Date(help="Starting invoice date", required=True)
    date_end = fields.Date(help="Ending invoice date", required=True)
    country_ids = fields.Many2many(
        comodel_name='res.country',
        relation='country_account_sold_qty_report_print_rel',
        column1='print_id',
        column2='country_id',
        string="Countries",
        required=True,
        help="Group these countries quantities into one column and the rest "
        + "of countries into another column",
    )
    company_id = fields.Many2one('res.company', required=True)
    digits = fields.Integer(default=0, help="Quantity precision")
    datas = fields.Binary("Data")

    @api.constrains('date_start', 'date_end')
    def _check_dates(self):
        for rec in self:
            if rec.date_start > rec.date_end:
                raise ValidationError(_("Date Start must be sooner than Date End!"))

    @api.constrains('digits')
    def _check_digits(self):
        for rec in self:
            if rec.digits < 0:
                raise ValidationError(_("Digits must be 0 or greater!"))

    def action_print(self):
        self.ensure_one()
        self.datas = self._generate_report_csv_base64_data()
        filename = FILENAME_PATTERN.format(
            self.date_start.strftime(DT_FMT),
            self.date_end.strftime(DT_FMT),
        )
        return {
            'type': 'ir.actions.act_url',
            'url': (
                f'/web/content/{self._name}/{self.id}/'
                + f'{FIELDNAME}/{filename}?download=true'
            ),
        }

    def _generate_report_csv_base64_data(self):
        self.ensure_one()
        country_codes = self.country_ids.mapped('code')
        data = self.env['account.sold.qty.report'].generate_report_data(
            self.date_start,
            self.date_end,
            country_codes,
            self.digits,
            self.company_id.id,
        )
        try:
            header = data[0].keys()
        except IndexError:
            raise ValidationError("No data found to print!")
        file = StringIO()
        writer = csv.DictWriter(file, header)
        writer.writeheader()
        writer.writerows(data)
        return base64.b64encode(file.getvalue().encode())
