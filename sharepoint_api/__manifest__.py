# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "MS Sharepoint API",
    'version': '16.0.1.0.0',
    'summary': 'Base integration with MS sharepoint',
    'license': 'OEEL-1',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'depends': [
        # oerp-odoo
        'http_client',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/sharepoint_site_security.xml',
        'views/menus.xml',
        'views/sharepoint_auth.xml',
        'views/sharepoint_site.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'api_sharepoint/static/src/js/error_dialogs.esm.js',
        ],
    },
    'installable': True,
}
