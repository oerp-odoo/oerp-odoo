# Author: Andrius Laukavičius. Copyright: JSC Focusate.
# See LICENSE file for full copyright and licensing details.
{
    'name': "QWeb Template Utilities",
    'version': '15.0.1.1.0',
    'summary': 'Helpers for QWeb templates',
    'license': 'LGPL-3',
    'author': "Focusate",
    'website': "http://www.focusate.eu",
    'category': 'Extra Tools',
    'depends': [
        # odoo
        'web'
    ],
    'data': [
        'templates/assets.xml',
        'templates/layouts.xml',
        'templates/base_templates.xml',
    ],
    'installable': False,
}
