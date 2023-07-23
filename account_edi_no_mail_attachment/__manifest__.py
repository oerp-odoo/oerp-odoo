# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Account EDI - Not in Mail Attachments",
    'version': '15.0.1.0.0',
    'summary': 'Do not include EDI XML in mail attachment',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'category': 'Hidden/Tools',
    'depends': [
        # oerp-odoo
        'account_edi',
    ],
    'data': [
        'views/res_config_settings_views.xml',
    ],
    'installable': False,
}
