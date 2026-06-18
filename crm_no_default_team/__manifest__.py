# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "CRM - No Default Team",
    'version': '19.0.1.0.0',
    'summary': 'Not set default team when creating lead/opportunity',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'depends': [
        # odoo
        'crm',
    ],
    'data': [
        'views/res_config_settings.xml',
    ],
    'installable': True,
}
