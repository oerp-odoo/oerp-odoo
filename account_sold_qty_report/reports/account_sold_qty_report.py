from odoo import models
from odoo.tools.float_utils import float_repr


class AccountSoldQtyReport(models.AbstractModel):
    _name = 'account.sold.qty.report'
    _description = "Account Sold Quantities Report"

    def generate_report_data(
        self, date_start, date_end, country_codes, digits, company_id
    ):
        amls = self._find_account_move_lines(date_start, date_end, company_id)
        return self._prepare_rows(amls, country_codes, digits)

    def _find_account_move_lines(self, date_start, date_end, company_id):
        domain = self._prepare_account_move_lines_domain(
            date_start, date_end, company_id
        )
        return self.env['account.move.line'].search(domain)

    def _prepare_account_move_lines_domain(self, date_start, date_end, company_id):
        # TODO: handle reversals.
        return [
            ('move_id.state', '=', 'posted'),
            ('move_id.move_type', '=', 'out_invoice'),
            ('move_id.company_id', '=', company_id),
            ('move_id.partner_id.country_id', '!=', False),
            ('display_type', '=', False),
            ('date', '>=', date_start),
            ('date', '<=', date_end),
            ('product_id', '!=', False),
            ('product_id.type', '=', 'product'),
            ('product_id.default_code', '!=', False),
        ]

    def _prepare_rows(self, amls, country_codes, digits):
        datas = {}
        for aml in amls:
            self._set_aml_data(datas, aml, country_codes)
        rows = []
        row_main_key = f"{', '.join(country_codes)} Quantity"
        row_other_key = 'Other Quantity'
        for product_code, qty_groups in datas.items():
            rows.append(
                {
                    'code': product_code,
                    row_main_key: float_repr(
                        qty_groups['main'], precision_digits=digits
                    ),
                    row_other_key: float_repr(
                        qty_groups['other'], precision_digits=digits
                    ),
                }
            )
        return rows

    def _set_aml_data(self, datas, aml, country_codes):
        country_code = aml.move_id.partner_id.country_id.code
        product_code = aml.product_id.default_code
        datas.setdefault(product_code, self._init_quantity_groups())
        qty_key = 'main' if country_code in country_codes else 'other'
        datas[product_code][qty_key] += aml.quantity

    def _init_quantity_groups(self):
        return {'main': 0, 'other': 0}
