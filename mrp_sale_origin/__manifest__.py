# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "MRP - Sale Source",
    'version': '15.0.1.0.0',
    'summary': 'Show Sale Source on related manufacturing order',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'category': 'Sale/Sale',
    'depends': [
        # odoo
        'sale_mrp',
    ],
    'data': ['views/mrp_production_views.xml'],
    'installable': True,
}
