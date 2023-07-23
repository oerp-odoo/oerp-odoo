# Author: Andrius Laukavičius. Copyright: JSC Focusate.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Invoices Custom QWeb Email Templates",
    'version': '15.0.1.1.0',
    'summary': 'Invoicing templates using QWeb inheritance',
    'license': 'LGPL-3',
    'author': "Focusate",
    'website': "http://www.focusate.eu",
    'category': 'Accounting/Invoicing',
    'depends': [
        # odoo
        'account',
        # oerp-odoo
        'mail_template_qweb_view',
    ],
    'data': [
        'templates/account_mail.xml',
        'data/mail_template.xml',
    ],
    'installable': False,
}
