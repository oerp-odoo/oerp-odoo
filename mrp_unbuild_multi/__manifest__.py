# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "MRP - Multi Unbuild",
    'version': '15.0.1.1.0',
    'summary': 'Unbuild multiple manufacturing orders at once',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'category': 'Manufacturing/Manufacturing',
    'depends': [
        # odoo
        'mrp',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizards/mrp_unbuild_multi_views.xml',
        'wizards/mrp_unbuild_multi_summary_views.xml',
    ],
    'installable': True,
}
