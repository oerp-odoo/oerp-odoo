# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Stock Picking Selling Price",
    'version': '15.0.2.0.0',
    'summary': 'stock, picking, move, selling price',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'category': 'Warehouse/Warehouse',
    'depends': [
        # odoo
        'stock',
    ],
    'data': [
        'views/stock_picking_views.xml',
        'reports/report_delivery_slip.xml',
    ],
    'installable': True,
}
