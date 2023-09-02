# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Purchase - No quick create on form",
    'version': '15.0.1.0.0',
    'summary': 'Will not show quick create option on some on some fields',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'category': 'Inventory/Purchase',
    'depends': [
        # odoo
        'purchase',
    ],
    'data': ['views/purchase_order_views.xml'],
    'installable': True,
}
