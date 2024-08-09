# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "HTTP Client Demo",
    'version': '17.0.4.0.0',
    'icon': '/odootil/static/description/icon.png',
    'summary': 'http, client, manager, demo',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'depends': [
        # oerp-odoo
        'http_client',
        'auth_menus',
    ],
    'data': [
        'security/http_client_demo_groups.xml',
        'security/ir.model.access.csv',
        'security/test_models_security.xml',
        'views/test_client_auth_views.xml',
    ],
    'installable': True,
}
