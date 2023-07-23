# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Fiscal Position B2C/B2B Notes",
    'version': '15.0.2.0.0',
    'summary': 'Notes per fiscal position for B2C/B2B purposes',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'category': 'Accounting/Fiscal Position',
    'depends': [
        # odoo
        'account',
    ],
    'data': [
        'views/account_fiscal_position_views.xml',
    ],
    'installable': False,
}
