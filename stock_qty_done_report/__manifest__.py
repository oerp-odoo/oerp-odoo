# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Stock - export done quantity per picking",
    'version': '15.0.1.0.0',
    'summary': 'Will export delivered products with quantity as CSV file',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'category': 'Inventory/Inventory',
    'depends': [
        # odoo
        'stock',
    ],
    'data': [
        'data/ir_actions_server.xml',
    ],
    'installable': True,
}
