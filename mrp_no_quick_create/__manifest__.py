# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "MRP - No quick create on form",
    'version': '15.0.1.0.0',
    'summary': 'Will not show quick create option on some fields',
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
        'views/mrp_bom_views.xml',
    ],
    'installable': True,
}
