# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "MRP - View Changes",
    'version': '15.0.1.0.0',
    'summary': 'Quality of life MRP view changes',
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
        'views/mrp_unbuild_views.xml',
    ],
    'installable': True,
}
