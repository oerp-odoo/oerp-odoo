# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Base Rest - Basic Auth",
    'version': '15.0.1.0.0',
    'summary': 'Integrate Basic Auth with open api docs',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'depends': [
        # oca:rest-framework
        'base_rest',
        'auth_basic',
    ],
    'installable': True,
    'auto_install': True,
}
