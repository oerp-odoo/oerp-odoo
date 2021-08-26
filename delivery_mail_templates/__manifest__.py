# Author: Andrius Laukavičius. Copyright: JSC Focusate.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Delivery Custom QWeb Email Templates",
    'version': '12.0.1.0.0',
    'summary': 'Delivery jinja2 templates rewritten to QWeb templates',
    'license': 'AGPL-3',
    'author': "Focusate",
    'website': "http://www.focusate.eu",
    'category': 'Stock',
    'depends': [
        # odoo
        'delivery',
        # oca-social
        'email_template_qweb',
        # oerp-odoo
        'base_templates',
    ],
    'data': [
        'templates/delivery_mail_templates.xml',
        'data/mail_data.xml',
    ],
    'installable': True,
}
