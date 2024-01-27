# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Stock Move Line Date in View",
    'version': '15.0.1.0.0',
    'summary': 'Show Date field in stock move line view via picking',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'category': 'Inventory/Inventory',
    'depends': [
        # odoo
        'stock',
    ],
    'data': ['views/stock_move_line_views.xml'],
    'installable': True,
}
