# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Apps View Changes",
    'version': '15.0.2.0.0',
    'summary': 'apps, modules, view changes',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'category': 'Hidden/Tools',
    'depends': [
        # odoo
        'base',
    ],
    'data': [
        'views/ir_module_views.xml',
    ],
    'auto_install': False,
    'installable': False,
}
