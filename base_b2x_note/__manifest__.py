# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "B2C/B2B Notes",
    'version': '15.0.2.0.0-rc.1',
    'summary': 'Notes per company for B2C/B2B purposes',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'category': 'Hidden/Tools',
    'depends': [
        # odoo
        'base',
    ],
    'data': [
        'views/res_company_views.xml',
    ],
    'installable': False,
}
