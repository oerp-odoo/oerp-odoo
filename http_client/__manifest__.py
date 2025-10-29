# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "HTTP Client",
    'version': '19.0.6.0.0',
    'summary': 'http, client, manager',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'depends': [
        # odoo
        'web',
    ],
    'data': [
        'security/regular_client_auth_security.xml',
        'security/ir.model.access.csv',
        'views/menus.xml',
        'views/http_client_auth.xml',
        'views/regular_client_auth.xml',
        'views/http_client_config.xml',
        'views/http_client_log.xml',
    ],
    'external_dependencies': {'python': ['mergedeep', 'validators', 'footil']},
    'assets': {
        'web.assets_backend': [
            'http_client/static/src/js/error_dialogs.esm.js',
        ],
    },
    'installable': True,
}
