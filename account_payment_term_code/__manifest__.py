# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Payment Terms Code",
    'version': '15.0.1.0.0',
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
        'views/account_payment_term_views.xml',
    ],
    'installable': True,
}
