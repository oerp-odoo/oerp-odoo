# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Payment Terms Code",
    'version': '19.0.2.0.0',
    'summary': 'Identifier for payment terms',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'category': 'Accounting/Accounting',
    'depends': [
        # odoo
        'account',
    ],
    'data': [
        'views/account_payment_term.xml',
    ],
    'installable': True,
}
