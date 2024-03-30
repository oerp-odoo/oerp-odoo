# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Basic HTTP Authentication",
    'version': '15.0.1.0.0',
    'summary': 'auth, basic, http, user, password',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'category': 'Hidden/Auth',
    'depends': [
        'auth_menus',
        # oca:server-env
        'server_environment',
    ],
    'external_dependencies': {'python': ['footil']},
    'data': ['security/ir.model.access.csv', 'views/auth_basic_views.xml'],
    'installable': True,
}
