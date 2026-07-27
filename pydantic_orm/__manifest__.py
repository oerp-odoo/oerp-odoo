# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Pydantic ORM",
    'version': '19.0.1.0.0',
    'summary': 'Convert Odoo records to pydantic and pydantic to odoo values',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'depends': ['base'],
    'external_dependencies': {
        'python': [
            'pydantic>2.0.0',
        ]
    },
    'installable': True,
}
