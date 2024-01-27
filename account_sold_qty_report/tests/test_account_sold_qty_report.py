import csv
import base64
from io import StringIO
from datetime import date, timedelta

from odoo.tests.common import tagged

from .common import TestAccountSoldQtyReportCommon


def _read_row(datas):
    bdatas = base64.b64decode(datas)
    sdatas = bdatas.decode()
    for row in csv.DictReader(StringIO(sdatas), delimiter=','):
        yield row


@tagged('post_install', '-at_install')
class TestAccountSoldQtyReport(TestAccountSoldQtyReportCommon):
    def test_01_account_sold_qty_report_lt_vs_other(self):
        # GIVEN
        wiz = self.AccountSoldQtyReportPrint.create(
            {
                'country_ids': [(6, 0, self.country_lt.ids)],
                'date_start': '2021-02-01',
                'date_end': '2021-02-28',
            }
        )
        # WHEN
        res = wiz.action_print()
        # THEN
        self.assertEqual(
            res,
            {
                'type': 'ir.actions.act_url',
                'url': (
                    f'/web/content/{wiz._name}/{wiz.id}/'
                    + 'datas/report.csv?download=true'
                ),
            },
        )
        rows_gen = _read_row(wiz.datas)
        map_ = {}
        row_1 = next(rows_gen)
        map_[row_1['code']] = row_1
        row_2 = next(rows_gen)
        map_[row_2['code']] = row_2
        with self.assertRaises(StopIteration):
            next(rows_gen)
        self.assertEqual(
            map_['glass'],
            # Quantity will be string when reading from csv.
            {'code': 'glass', 'LT Quantity': '3', 'Other Quantity': '7'},
        )
        self.assertEqual(
            map_['bucket'],
            {'code': 'bucket', 'LT Quantity': '30', 'Other Quantity': '70'},
        )

    def test_02_account_sold_qty_report_lt_only(self):
        # GIVEN
        wiz = self.AccountSoldQtyReportPrint.create(
            {
                'country_ids': [(6, 0, self.country_lt.ids)],
                'date_start': '2021-02-01',
                'date_end': '2021-02-02',
            }
        )
        # WHEN
        res = wiz.action_print()
        # THEN
        self.assertEqual(
            res,
            {
                'type': 'ir.actions.act_url',
                'url': (
                    f'/web/content/{wiz._name}/{wiz.id}/'
                    + 'datas/report.csv?download=true'
                ),
            },
        )
        rows_gen = _read_row(wiz.datas)
        map_ = {}
        row_1 = next(rows_gen)
        map_[row_1['code']] = row_1
        row_2 = next(rows_gen)
        map_[row_2['code']] = row_2
        with self.assertRaises(StopIteration):
            next(rows_gen)
        self.assertEqual(
            map_['glass'],
            {'code': 'glass', 'LT Quantity': '3', 'Other Quantity': '0'},
        )
        self.assertEqual(
            map_['bucket'],
            {'code': 'bucket', 'LT Quantity': '30', 'Other Quantity': '0'},
        )

    def test_03_account_sold_qty_report_print_defaults(self):
        # GIVEN
        self.company_main.country_id = self.country_lt.id
        # WHEN
        wiz = self.AccountSoldQtyReportPrint.create({})
        # THEN
        self.assertEqual(wiz.country_ids, self.country_lt)
        today = date.today()
        dt_last_month_end = today.replace(day=1) - timedelta(days=1)
        dt_start = dt_last_month_end.replace(day=1)
        self.assertEqual(wiz.date_start, dt_start)
        self.assertEqual(wiz.date_end, dt_last_month_end)
