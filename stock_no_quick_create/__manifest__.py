# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Stock - No quick create on form",
    'version': '15.0.1.0.0',
    'summary': 'Will not show quick create option on some fields',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'category': 'Inventory/Purchase',
    'depends': [
        # odoo
        'stock',
    ],
    'data': ['views/stock_move_line_views.xml'],
    'installable': True,
}
