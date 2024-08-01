# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Stock - Conditional MTO",
    'version': '15.0.1.1.0',
    'summary': 'Trigger MTO procurement instead of MTS depending on conditions',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'category': 'Inventory/Inventory',
    'depends': [
        # odoo
        'stock',
    ],
    'data': [
        'views/stock_location_route_views.xml',
    ],
    'installable': True,
}
