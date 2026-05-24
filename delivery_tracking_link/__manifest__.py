# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Custom Delivery Tracking Links",
    'version': '19.0.3.0.0',
    'summary': 'delivery, stock, tracking',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'category': 'Inventory/Delivery',
    'depends': [
        # odoo
        'stock_delivery',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/delivery_tracking_link.xml',
        'views/delivery_carrier.xml',
        'views/stock_picking.xml',
    ],
    'demo': ['demo/delivery_tracking_link.xml'],
    'installable': True,
}
