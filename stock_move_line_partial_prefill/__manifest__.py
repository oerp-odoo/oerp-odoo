# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Partially Prefill Detailed Operations",
    'version': '15.0.1.0.0',
    'summary': 'stock, inventory, move line, partial, prefill, confirm',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'category': 'Inventory/Inventory',
    'depends': [
        # odoo
        'stock',
    ],
    'data': [
        'views/stock_picking_type_views.xml',
    ],
    'installable': False,
}
