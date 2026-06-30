# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "MRP - View Changes",
    'version': '19.0.2.0.0',
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
        'views/mrp_production.xml',
        'views/mrp_unbuild.xml',
    ],
    'installable': True,
}
