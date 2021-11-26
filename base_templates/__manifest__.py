# Author: Andrius Laukavičius. Copyright: JSC Focusate.
# See LICENSE file for full copyright and licensing details.
{
    'name': "QWeb Template Utilities",
    'version': '15.0.1.1.0',
    'summary': 'Helpers for QWeb templates',
    'license': 'LGPL-3',
    'author': "Focusate",
    'website': "http://www.focusate.eu",
    'category': 'Hidden/Tools',
    'depends': [
        # odoo
        'web',
    ],
    'data': [
        'templates/layouts.xml',
        'templates/base_templates.xml',
    ],
    'assets': {
        'web.assets_backend': [
            '/base_templates/static/src/scss/assets.scss',
        ],
    },
    'installable': True,
}
