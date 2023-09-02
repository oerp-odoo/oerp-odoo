# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Sale - No quick create on form",
    'version': '15.0.1.0.0',
    'summary': 'Will not show quick create option on some sale form fields',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'category': 'Sale/Sale',
    'depends': [
        # odoo
        'sale',
    ],
    'data': ['views/sale_order_views.xml'],
    'installable': True,
}
