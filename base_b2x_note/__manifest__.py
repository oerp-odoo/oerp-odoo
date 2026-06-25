# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "B2C/B2B Notes",
    'version': '19.0.3.0.0',
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
        'views/res_company.xml',
    ],
    'installable': True,
}
