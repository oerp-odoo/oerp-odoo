from odoo.osv import expression

import datetime

from odoo import models


class StockPMoveOperationReport(models.AbstractModel):
    _name = 'stock.move.operation.report'
    _description = "Stock Move Operation Report"

    def generate_report_data(
        self,
        date_start,
        date_end,
        company_id,
        warehouse=None,
        product_ids=None,
    ):
        products = self._find_products(company_id, product_ids=product_ids)
        # Same products, but with different to_date in context, to return
        # starting quantity or ending quantity.
        products_start = products.with_context(
            self._prepare_product_qty_context(date_start, warehouse=warehouse)
        )
        products_end = products.with_context(
            self._prepare_product_qty_context(date_end, warehouse=warehouse)
        )
        rows = []
        op_usage_map = self._get_operation_usage_map()
        for (product_start, product_end) in zip(products_start, products_end):
            rows.append(
                self._prepare_row_data(
                    product_start,
                    product_end,
                    date_start,
                    date_end,
                    op_usage_map,
                    warehouse=warehouse,
                )
            )
        return rows

    def _find_products(self, company_id, product_ids=None):
        domain = self._get_products_domain(company_id, product_ids=product_ids)
        return self.env['product.product'].search(domain)

    def _get_products_domain(self, company_id, product_ids=None):
        domain = [
            ('type', 'in', ('product', 'consu')),
            ('company_id', 'in', (company_id, False)),
        ]
        if product_ids is not None:
            domain.append(('id', 'in', product_ids))
        return domain

    def _prepare_row_data(
        self,
        product_start,
        product_end,
        date_start,
        date_end,
        op_usage_map,
        warehouse=None,
    ):
        operation_totals = self._init_operation_totals()
        for op, qty in self._get_operation_with_qty(
            product_start,
            date_start,
            date_end,
            op_usage_map,
            warehouse=warehouse,
        ):
            operation_totals[op] += qty
        return {
            'product_code': product_start.default_code,
            'quantity_start': product_start.qty_available,
            **operation_totals,
            'quantity_end': product_end.qty_available,
        }

    def _get_operation_with_qty(
        self, product, date_start, date_end, op_usage_map, warehouse=None
    ):
        domain = self._get_stock_moves_domain(
            product, date_start, date_end, warehouse=warehouse
        )
        moves = self.env['stock.move'].search(domain)
        for move in moves:
            op = op_usage_map[
                (move.location_id.usage, move.location_dest_id.usage)
            ]
            yield (op, move.product_uom_qty)

    def _get_stock_moves_domain(
        self, product, date_start, date_end, warehouse=None
    ):
        def get_extra_domain():
            domain_src_internal = [
                ('location_id.usage', '=', 'internal'),
                ('location_dest_id.usage', '!=', 'internal'),
            ]
            domain_dest_internal = [
                ('location_id.usage', '!=', 'internal'),
                ('location_dest_id.usage', '=', 'internal'),
            ]
            if warehouse:
                location_id = warehouse.lot_stock_id.id
                domain_src_internal.append(
                    ('location_id', 'child_of', location_id)
                )
                domain_dest_internal.append(
                    ('location_dest_id', 'child_of', location_id)
                )
            return expression.OR([domain_src_internal, domain_dest_internal])

        base_domain = [
            ('product_id', '=', product.id),
            ('state', '=', 'done'),
            ('date', '>=', date_start),
            ('date', '<=', date_end),
        ]
        return expression.AND([base_domain, get_extra_domain()])

    def _get_operation_usage_map(self):
        return {
            # in/out is determined from internal location, not from
            # virtual location.
            ('production', 'internal'): 'manufacture_in',
            ('internal', 'production'): 'manufacture_out',
            ('supplier', 'internal'): 'purchase_in',
            ('internal', 'supplier'): 'purchase_out',
            ('customer', 'internal'): 'sell_in',
            ('internal', 'customer'): 'sell_out',
            ('inventory', 'internal'): 'inventory_in',
            ('internal', 'inventory'): 'inventory_out',
        }

    def _init_operation_totals(self):
        return {
            'manufacture_in': 0,
            'manufacture_out': 0,
            'purchase_in': 0,
            'purchase_out': 0,
            'sell_in': 0,
            'sell_out': 0,
            'inventory_in': 0,
            'inventory_out': 0,
        }

    def _prepare_product_qty_context(self, to_date, warehouse=None):
        ctx = {
            'to_date': datetime.datetime(
                to_date.year, to_date.month, to_date.day
            )
        }
        if warehouse:
            ctx['warehouse'] = warehouse.id
        return ctx
