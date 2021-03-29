# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Custom Delivery Tracking Links",
    'version': '12.0.1.0.0',
    'summary': 'delivery, stock, tracking',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'category': 'Warehouse',
    'depends': ['delivery'],
    'data': [
        'security/ir.model.access.csv',
        'views/delivery_tracking_link_views.xml',
        'views/delivery_carrier_views.xml',
    ],
    'demo': ['demo/delivery_tracking_link_demo.xml'],
}
