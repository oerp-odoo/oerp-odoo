# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "HTTP Client",
    'version': '16.0.3.0.0',
    'summary': 'http, client, manager',
    'license': 'OEEL-1',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'depends': [
        # odoo
        'web',
    ],
    'data': [
        'security/regular_client_auth_security.xml',
        'security/ir.model.access.csv',
        'views/http_client_auth_views.xml',
        'views/regular_client_auth_views.xml',
    ],
    'external_dependencies': {'python': ['mergedeep']},
    'assets': {
        'web.assets_backend': [
            'http_client/static/src/js/error_dialogs.esm.js',
        ],
    },
    'installable': True,
}
