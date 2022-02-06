# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Developer Mode on Login",
    'version': '14.0.2.0.0',
    'summary': 'Automatically enable developer mode when logging in',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'category': 'Hidden/Tools',
    'depends': [
        'web',
    ],
    'data': [
        'data/res_users_data.xml',
        'views/res_users_views.xml',
    ],
    'auto_install': True,
    'installable': True,
}
