# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Purchase Effective Date in List View",
    'version': '19.0.2.0.0',
    'summary': 'Adds Effective Date in List View',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'category': 'Inventory/Purchase',
    'depends': [
        # odoo
        'purchase_stock',
    ],
    'data': [
        'views/purchase_order.xml',
    ],
    'installable': True,
}
