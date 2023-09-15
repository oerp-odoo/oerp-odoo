# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Purchase Confirmation Date in RQF List View",
    'version': '15.0.1.1.0',
    'summary': 'Adds Confirmation Date in RFQ List View',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'category': 'Inventory/Purchase',
    'depends': [
        # odoo
        'purchase',
    ],
    'data': [
        'views/purchase_order_views.xml',
    ],
    'installable': True,
}
