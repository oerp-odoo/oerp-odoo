# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Github API",
    'version': '17.0.1.0.0',
    'summary': 'Base integration with Github',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'depends': [
        # oerp-odoo
        'http_client',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/github_repo_security.xml',
        'views/menus.xml',
        'views/github_auth.xml',
        'views/github_repo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'github_api/static/src/js/error_dialogs.esm.js',
        ],
    },
    'installable': True,
}
