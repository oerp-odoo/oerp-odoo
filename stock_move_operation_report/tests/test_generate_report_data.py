import datetime

from odoo.tests.common import tagged

from .common import TestStockMoveOperationReportCommon


@tagged('post_install', '-at_install')
class TestGenerateReportData(TestStockMoveOperationReportCommon):
    def test_01_generate_report_data_with_warehouse(self):
        # GIVEN
        # Add glass product moves.
        # 10 manufactured at the start of period
        self.make_stock_move(
            self.product_glass,
            10,
            self.stock_location_production,
            self.stock_location_stock,
            lines=[(10, None)],
            dt=datetime.date(2022, 2, 1),
        )
        # 3 more bought in period.
        self.make_stock_move(
            self.product_glass,
            3,
            self.stock_location_suppliers,
            self.stock_location_stock,
            lines=[(3, None)],
            dt=datetime.date(2022, 2, 10),
        )
        # 2 sold in period
        self.make_stock_move(
            self.product_glass,
            2,
            self.stock_location_stock,
            self.stock_location_customers,
            lines=[(2, None)],
            dt=datetime.date(2022, 2, 11),
        )
        # 2 scrapped in period
        self.make_stock_move(
            self.product_glass,
            2,
            self.stock_location_stock,
            self.stock_location_scrap,
            lines=[(2, None)],
            dt=datetime.date(2022, 2, 11),
        )
        # 1 unscrapped in period
        self.make_stock_move(
            self.product_glass,
            1,
            self.stock_location_scrap,
            self.stock_location_stock,
            lines=[(1, None)],
            dt=datetime.date(2022, 2, 13),
        )
        # 1 manufacture consumed (raw material or unbuilt)
        self.make_stock_move(
            self.product_glass,
            1,
            self.stock_location_stock,
            self.stock_location_production,
            lines=[(1, None)],
            dt=datetime.date(2022, 2, 11),
        )
        # 5 sold after period
        self.make_stock_move(
            self.product_glass,
            5,
            self.stock_location_stock,
            self.stock_location_customers,
            lines=[(5, None)],
            dt=datetime.date(2022, 3, 1),
        )
        # Add bucket product moves.
        # 5 manufactured before period
        self.make_stock_move(
            self.product_bucket,
            5,
            self.stock_location_production,
            self.stock_location_stock,
            lines=[(5, None)],
            dt=datetime.date(2022, 1, 20),
        )
        # 3 sold in period
        self.make_stock_move(
            self.product_bucket,
            3,
            self.stock_location_stock,
            self.stock_location_customers,
            lines=[(3, None)],
            dt=datetime.date(2022, 2, 12),
        )
        # 1 sell returned in period
        self.make_stock_move(
            self.product_bucket,
            1,
            self.stock_location_customers,
            self.stock_location_stock,
            lines=[(1, None)],
            dt=datetime.date(2022, 2, 12),
        )
        # 1 bought in period
        self.make_stock_move(
            self.product_bucket,
            1,
            self.stock_location_suppliers,
            self.stock_location_stock,
            lines=[(1, None)],
            dt=datetime.date(2022, 2, 13),
        )
        # 1 purchase returned in period
        self.make_stock_move(
            self.product_bucket,
            1,
            self.stock_location_stock,
            self.stock_location_suppliers,
            lines=[(1, None)],
            dt=datetime.date(2022, 2, 13),
        )
        # 2 transit in, in period
        self.make_stock_move(
            self.product_bucket,
            2,
            self.stock_location_transit,
            self.stock_location_stock,
            lines=[(2, None)],
            dt=datetime.date(2022, 2, 13),
        )
        # 2 transit out in period
        self.make_stock_move(
            self.product_bucket,
            2,
            self.stock_location_stock,
            self.stock_location_transit,
            lines=[(2, None)],
            dt=datetime.date(2022, 2, 14),
        )
        # WHEN
        res = self.StockPMoveOperationReport.generate_report_data(
            datetime.date(2022, 2, 1),
            datetime.date(2022, 2, 28),
            company_id=self.company_main.id,
            warehouse=self.warehouse_1,
            product_ids=[self.product_glass.id, self.product_bucket.id],
        )
        # THEN
        self.assertEqual(len(res), 2)
        self.assertEqual(
            sorted(res, key=lambda x: x['product_code']),
            sorted(
                [
                    {
                        'product_name': 'Glass',
                        'product_code': 'glass',
                        'quantity_start': 10,
                        'manufacture_in': 10,
                        'manufacture_out': 1,
                        'purchase_in': 3,
                        'purchase_out': 0,
                        'sell_in': 0,
                        'sell_out': 2,
                        'inventory_in': 1,
                        'inventory_out': 2,
                        'transit_in': 0,
                        'transit_out': 0,
                        # 'sold': 10,
                        # 'scrapped': 10,
                        # 10 + 3 - 2 - 2 + 1 - 1 = 9 (5 sold is outside period)
                        'quantity_end': 9,
                    },
                    {
                        'product_name': 'Bucket',
                        'product_code': 'bucket',
                        'quantity_start': 5,
                        'manufacture_in': 0,
                        'manufacture_out': 0,
                        'purchase_in': 1,
                        'purchase_out': 1,
                        'sell_in': 1,
                        'sell_out': 3,
                        'inventory_in': 0,
                        'inventory_out': 0,
                        'transit_in': 2,
                        'transit_out': 2,
                        # 5 - 3 + 1 + 1 - 1 + 2 - 2 = 3
                        'quantity_end': 3,
                    },
                ],
                key=lambda x: x['product_code'],
            ),
        )

    def test_02_generate_report_data_without_warehouse(self):
        # GIVEN
        # Add glass product moves.
        # 10 manufactured at the start of period
        self.make_stock_move(
            self.product_glass,
            10,
            self.stock_location_production,
            self.stock_location_stock,
            lines=[(10, None)],
            dt=datetime.date(2022, 2, 1),
        )
        # 3 more bought in period.
        self.make_stock_move(
            self.product_glass,
            3,
            self.stock_location_suppliers,
            self.stock_location_stock,
            lines=[(3, None)],
            dt=datetime.date(2022, 2, 10),
        )
        # 2 sold in period
        self.make_stock_move(
            self.product_glass,
            2,
            self.stock_location_stock,
            self.stock_location_customers,
            lines=[(2, None)],
            dt=datetime.date(2022, 2, 11),
        )
        # 2 scrapped in period
        self.make_stock_move(
            self.product_glass,
            2,
            self.stock_location_stock,
            self.stock_location_scrap,
            lines=[(2, None)],
            dt=datetime.date(2022, 2, 11),
        )
        # 1 unscrapped in period
        self.make_stock_move(
            self.product_glass,
            1,
            self.stock_location_scrap,
            self.stock_location_stock,
            lines=[(1, None)],
            dt=datetime.date(2022, 2, 13),
        )
        # 1 manufacture consumed (raw material or unbuilt)
        self.make_stock_move(
            self.product_glass,
            1,
            self.stock_location_stock,
            self.stock_location_production,
            lines=[(1, None)],
            dt=datetime.date(2022, 2, 11),
        )
        # 5 sold after period
        self.make_stock_move(
            self.product_glass,
            5,
            self.stock_location_stock,
            self.stock_location_customers,
            lines=[(5, None)],
            dt=datetime.date(2022, 3, 1),
        )
        # Add bucket product moves.
        # 5 manufactured before period
        self.make_stock_move(
            self.product_bucket,
            5,
            self.stock_location_production,
            self.stock_location_stock,
            lines=[(5, None)],
            dt=datetime.date(2022, 1, 20),
        )
        # 3 sold in period
        self.make_stock_move(
            self.product_bucket,
            3,
            self.stock_location_stock,
            self.stock_location_customers,
            lines=[(3, None)],
            dt=datetime.date(2022, 2, 12),
        )
        # 1 sell returned in period
        self.make_stock_move(
            self.product_bucket,
            1,
            self.stock_location_customers,
            self.stock_location_stock,
            lines=[(1, None)],
            dt=datetime.date(2022, 2, 12),
        )
        # 1 bought in period
        self.make_stock_move(
            self.product_bucket,
            1,
            self.stock_location_suppliers,
            self.stock_location_stock,
            lines=[(1, None)],
            dt=datetime.date(2022, 2, 13),
        )
        # 1 purchase returned in period
        self.make_stock_move(
            self.product_bucket,
            1,
            self.stock_location_stock,
            self.stock_location_suppliers,
            lines=[(1, None)],
            dt=datetime.date(2022, 2, 13),
        )
        # WHEN
        res = self.StockPMoveOperationReport.generate_report_data(
            datetime.date(2022, 2, 1),
            datetime.date(2022, 2, 28),
            company_id=self.company_main.id,
            product_ids=[self.product_glass.id, self.product_bucket.id],
        )
        # THEN
        self.assertEqual(len(res), 2)
        self.assertEqual(
            sorted(res, key=lambda x: x['product_code']),
            sorted(
                [
                    {
                        'product_name': 'Glass',
                        'product_code': 'glass',
                        'quantity_start': 10,
                        'manufacture_in': 10,
                        'manufacture_out': 1,
                        'purchase_in': 3,
                        'purchase_out': 0,
                        'sell_in': 0,
                        'sell_out': 2,
                        'inventory_in': 1,
                        'inventory_out': 2,
                        'transit_in': 0,
                        'transit_out': 0,
                        # 'sold': 10,
                        # 'scrapped': 10,
                        # 10 + 3 - 2 - 2 + 1 - 1 = 9 (5 sold is outside period)
                        'quantity_end': 9,
                    },
                    {
                        'product_name': 'Bucket',
                        'product_code': 'bucket',
                        'quantity_start': 5,
                        'manufacture_in': 0,
                        'manufacture_out': 0,
                        'purchase_in': 1,
                        'purchase_out': 1,
                        'sell_in': 1,
                        'sell_out': 3,
                        'inventory_in': 0,
                        'inventory_out': 0,
                        'transit_in': 0,
                        'transit_out': 0,
                        # 5 - 3 + 1 + 1 - 1 = 3
                        'quantity_end': 3,
                    },
                ],
                key=lambda x: x['product_code'],
            ),
        )
