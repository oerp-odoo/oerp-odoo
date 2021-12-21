# Author: Andrius Laukavičius. Copyright: JSC Focusate.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Mail Template QWeb View",
    'version': '15.0.1.0.0',
    'summary': 'mail, template, qweb, inheritance',
    'license': 'LGPL-3',
    'author': "Focusate",
    'website': "http://www.focusate.eu",
    'category': 'Productivity/Discuss',
    'depends': [
        # odoo
        'mail',
    ],
    'data': [
        'views/mail_template_views.xml',
    ],
    'demo': [
        'demo/mail_template.xml',
    ],
    'installable': True,
}
