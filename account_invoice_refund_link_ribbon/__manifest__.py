# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Invoice Reversed Word on Ribbon",
    'version': '15.0.1.1.0',
    'summary': 'Shows reversed word on ribbon on paid and refunded invoice',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'category': 'Accounting/Accounting',
    'depends': [
        # oca-account-invoicing
        'account_invoice_refund_link',
    ],
    'data': [
        'views/account_move_views.xml',
    ],
    'installable': True,
}
