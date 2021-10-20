# Author: Andrius Laukavičius. Copyright: JSC Focusate.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Sale Custom QWeb Email Templates",
    'version': '15.0.1.1.0',
    'summary': 'Sales jinja2 templates rewritten to QWeb templates',
    'license': 'AGPL-3',
    'author': "Focusate",
    'website': "http://www.focusate.eu",
    'category': 'Sales',
    'depends': [
        # odoo
        'sale',
        # oca-social
        'email_template_qweb',
        # oerp-odoo
        'base_templates',
    ],
    'data': [
        'templates/sale_mail_templates.xml',
        'data/mail_data.xml',
    ],
    'installable': False,
}
