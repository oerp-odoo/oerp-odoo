# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Marketing Sample Sales",
    'version': '15.0.2.0.0',
    'summary': 'sale, order, marketing, sample',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'category': 'Sales/Marketing',
    'depends': [
        # odoo
        'sale_stock',
        'stock_picking_selling_price',
    ],
    'data': [
        'views/sale_order_views.xml',
        'views/account_move_views.xml',
        'views/stock_picking_views.xml',
        'reports/report_invoice.xml',
    ],
    'installable': True,
}
