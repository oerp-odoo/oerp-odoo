# Author: Andrius Laukavičius. Copyright: JSC Focusate.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Invoices Custom QWeb Email Templates",
    'version': '15.0.1.1.0',
    'summary': 'Invoices jinja2 templates rewritten to QWeb templates',
    'license': 'AGPL-3',
    'author': "Focusate",
    'website': "http://www.focusate.eu",
    'category': 'Accounting',
    'depends': [
        # odoo
        'account',
        # oca-social
        'email_template_qweb',
        # oerp-odoo
        'base_templates',
    ],
    'data': [
        'templates/account_mail_templates.xml',
        'data/mail_data.xml',
    ],
    'installable': False,
}
