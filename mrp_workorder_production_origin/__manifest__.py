# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "MRP Workorder - Manufacturing Source",
    'version': '15.0.1.0.0',
    'summary': 'Show Manufacturing order source on workorder',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'category': 'Manufacturing/Manufacturing',
    'depends': [
        # odoo
        'mrp',
    ],
    'data': ['views/mrp_workorder_views.xml'],
    'installable': True,
}
