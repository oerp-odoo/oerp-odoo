# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Purchase Effective Date in List View",
    'version': '15.0.1.1.0',
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
        'views/purchase_order_views.xml',
    ],
    'installable': False,
}
