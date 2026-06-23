# Author: Andrius Laukavičius. Copyright: Time for dev.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Mail Template QWeb View",
    'version': '19.0.2.0.0',
    'summary': 'mail, template, qweb, inheritance',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "http://timefordev.com",
    'category': 'Productivity/Discuss',
    'depends': [
        # odoo
        'mail',
    ],
    'data': [
        'views/mail_template_views.xml',
    ],
    'installable': True,
}
