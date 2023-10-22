# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Web - No quick create on form",
    'version': '15.0.1.0.0',
    'summary': 'Will not show quick create option on relation fields',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'category': 'Hidden/Tools',
    'depends': [
        # odoo
        'web',
        'base_setup',
    ],
    'data': [
        'views/res_config_settings_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'web_no_quick_create/static/src/js/relational_fields.js',
        ],
    },
    'installable': True,
}
