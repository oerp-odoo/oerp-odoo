# Author: Andrius Laukavičius. Copyright: JSC Focusate.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Delivery Custom QWeb Email Templates",
    'version': '15.0.1.1.0',
    'summary': 'Delivery templates using QWeb inheritance',
    'license': 'AGPL-3',
    'author': "Focusate",
    'website': "http://www.focusate.eu",
    'category': 'Inventory/Delivery',
    'depends': [
        # odoo
        'stock',
        # oerp-odoo
        'mail_template_qweb_view',
    ],
    'data': [
        'templates/delivery_mail_templates.xml',
        'data/mail_template.xml',
    ],
    'installable': True,
}
