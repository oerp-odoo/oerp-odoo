# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "MRP - Unbuild Relation",
    'version': '15.0.1.0.0',
    'summary': 'Show related unbuild orders on manufacturing orders',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'category': 'Manufacturing/Manufacturing',
    'depends': [
        # odoo
        'mrp',
    ],
    'data': [
        'views/mrp_production_views.xml',
    ],
    'installable': True,
}
