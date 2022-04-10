# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Purchase Effective Date in List View",
    'version': '15.0.1.0.0',
    'summary': 'Sales templates using QWeb inheritance',
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
    'installable': True,
}
