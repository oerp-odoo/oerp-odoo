# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': 'EORI Number',
    'version': '19.0.3.0.0',
    'summary': 'eori, partner, company',
    'license': 'LGPL-3',
    'author': 'Andrius Laukavičius',
    'website': 'https://timefordev.com',
    'category': 'Hidden/Tools',
    'depends': [
        # odoo
        'base',
    ],
    'data': [
        'views/res_company.xml',
        'views/res_partner.xml',
    ],
    'installable': True,
}
