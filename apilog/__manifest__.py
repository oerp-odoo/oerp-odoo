# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE and COPYRIGHT files for details.
{
    'name': 'API Logger',
    'version': '20.0.3.0.0',
    'summary': 'Base module to log incoming and outgoing requests within odoo',
    'license': 'LGPL-3',
    'author': 'Andrius Laukavičius',
    'website': 'https://timefordev.com',
    'category': 'Hidden/Tools',
    'depends': [
        'odootil',
    ],
    'data': [
        'security/ir.access.csv',
        'views/menus.xml',
        'views/apilog_log.xml',
        'views/apilog_config.xml',
        'views/apilog_label.xml',
    ],
    'installable': True,
}
