# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Delivery - 3PL",
    'version': '15.0.1.0.0',
    'summary': 'Helper module to integrate Odoo with 3PL platforms',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'category': 'Inventory/Delivery',
    'depends': [
        # odoo
        'delivery',
    ],
    'external_dependencies': {'python': ['footil', 'validators']},
    'installable': True,
}
