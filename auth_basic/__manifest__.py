# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Basic HTTP Authentication",
    'version': '19.0.2.0.0',
    'summary': 'auth, basic, http, user, password',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'depends': [
        'auth_menus',
        # oca:server-env
        'server_environment',
    ],
    'external_dependencies': {'python': ['footil']},
    'data': ['security/ir.model.access.csv', 'views/auth_basic.xml'],
    'installable': True,
}
