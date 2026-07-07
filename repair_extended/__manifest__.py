# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Repair - Extended",
    'version': '19.0.2.0.0',
    'summary': 'Extra features for repair module',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'category': 'Inventory/Inventory',
    'depends': [
        # odoo
        'repair',
    ],
    'data': [
        'views/repair_order.xml',
    ],
    'installable': True,
}
