# Author: Andrius Laukavičius. Copyright: JSC Focusate.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Sale Custom QWeb Email Templates",
    'version': '15.0.1.1.0',
    'summary': 'Sales templates using QWeb inheritance',
    'license': 'LGPL-3',
    'author': "Focusate",
    'website': "http://www.focusate.eu",
    'category': 'Sales/Sales',
    'depends': [
        # odoo
        'sale',
        # oerp-odoo
        'mail_template_qweb_view',
    ],
    'data': [
        'templates/sale_mail.xml',
        'data/mail_template.xml',
    ],
    'installable': False,
}
