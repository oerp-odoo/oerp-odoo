# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "MRP - Mass Produce Serials With Missing Components",
    'version': '15.0.1.0.0',
    'summary': 'Ignore missing components when mass producing serials',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'category': 'Manufacturing/Manufacturing',
    'depends': [
        # odoo
        'mrp',
    ],
    'data': [
        'views/stock_picking_type_views.xml',
    ],
    'installable': True,
}
