# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "API Base",
    'version': '15.0.1.0.0',
    'summary': 'Base API module to use for specific API implementations',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'category': 'Hidden/Tools',
    'depends': [
        'auth_basic',
        # oca-rest-framework
        'base_rest_pydantic',
        'extendable',
    ],
    'installable': True,
}
